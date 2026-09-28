"""Supporting functions for core.py, models.py, and train.py."""

import json
import re
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf
import torch
import torchaudio

from config import YAMNET_DIR
from models import WaveformModel


def load_waveform(
        path,
        sample_rate: int,
        num_samples: int
) -> torch.Tensor:
    data, sr = sf.read(path, dtype="float32")
    waveform = torch.from_numpy(data)

    if sr != sample_rate:
        waveform = torchaudio.functional.resample(waveform, sr, sample_rate)

    if waveform.shape[-1] < num_samples:
        waveform = torch.nn.functional.pad(waveform, (0, num_samples - waveform.shape[-1]))
    else:
        waveform = waveform[:num_samples]

    return waveform


def yamnet_filename_map() -> dict:
    mapping = {}
    for p in YAMNET_DIR.glob("*.hdf5"):
        match = re.match(r"stim\d+_cat\d+_([a-z]+)_exemp(\d+)\.hdf5", p.name)
        mapping[f"s2_{match.group(1)}_{int(match.group(2))}.wav"] = p
    return mapping


def resolve_device(
        requested: str = None
) -> torch.device:
    if requested is not None:
        return torch.device(requested)
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def confirm_device(
        device: torch.device
):
    if device.type == "cuda":
        print(f"Using GPU: {torch.cuda.get_device_name(device)} (CUDA)")
    elif device.type == "mps":
        print("Using GPU: Apple Silicon (MPS)")
    else:
        print("Using CPU.")
        if torch.cuda.is_available():
            print("Note: a CUDA GPU is available but not being used -- pass --device cuda.")
        elif torch.backends.mps.is_available():
            print("Note: an Apple Silicon (MPS) GPU is available but not being used -- pass --device mps.")


def run_epoch(
        model,
        loader,
        device,
        criterion,
        optimizer=None
):
    """ Runs one pass over `loader`; trains if `optimizer` is given, else evaluates.

    Args:
        model: Model to train or evaluate.
        loader: Yields (waveform, spectrogram, label) batches.
        device: Device to run on.
        criterion: Loss function.
        optimizer: If given, the model is trained (backward pass + step); otherwise it's only evaluated.

    Returns:
        Tuple of (average loss, accuracy) over the epoch.
    """
    model.train() if optimizer is not None else model.eval()

    total_loss, correct, total = 0.0, 0, 0
    with torch.set_grad_enabled(optimizer is not None):
        for waveform, spectrogram, label in loader:
            inputs = waveform if isinstance(model, WaveformModel) else spectrogram
            inputs, label = inputs.to(device), label.to(device)

            logits = model(inputs)
            loss = criterion(logits, label)

            if optimizer is not None:
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            total_loss += loss.item() * label.size(0)
            correct += (logits.argmax(dim=-1) == label).sum().item()
            total += label.size(0)

    return total_loss / total, correct / total


def next_run_id(
        checkpoint_dir: Path,
        model_name: str
) -> int:
    """ Smallest run id not yet used by a checkpoint of this model, so repeated runs don't overwrite each other.

    Args:
        checkpoint_dir: Directory to look for existing checkpoints in.
        model_name: Model type to check, e.g. "waveform".

    Returns:
        The smallest unused run id.
    """
    existing = checkpoint_dir.glob(f"{model_name}_run*_*.pt")
    run_ids = [int(match.group(1)) for p in existing if (match := re.match(rf"{model_name}_run(\d+)_", p.name))]
    return max(run_ids, default=-1) + 1


def train_model(
        model_name,
        model,
        train_loader,
        val_loader,
        args,
        device
):
    model = model.to(device)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"\n=== Training {model_name} ({n_params:,} parameters) ===")

    checkpoint_dir = Path(args.checkpoint_dir)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    run_id = next_run_id(checkpoint_dir, model_name)

    # save the best-so-far model on every val-accuracy improvement; cheap (one
    # overwritten file) so this always happens, unlike the opt-in checkpoints below
    best_val_acc = -1.0
    best_path = checkpoint_dir / f"{model_name}_run{run_id}_best.pt"
    history = {"train_loss": [], "train_acc": [], "val_loss": [], "val_acc": [], "best_epoch": None}
    history_path = checkpoint_dir / f"{model_name}_run{run_id}_history.json"

    checkpointing = bool(args.checkpoint_epochs)
    if checkpointing:
        # untrained weights, needed later to compare untrained vs. trained brain alignment
        torch.save(model.state_dict(), checkpoint_dir / f"{model_name}_run{run_id}_untrained.pt")

    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    criterion = torch.nn.CrossEntropyLoss()

    for epoch in range(1, args.epochs + 1):
        train_loss, train_acc = run_epoch(model, train_loader, device, criterion, optimizer)
        val_loss, val_acc = run_epoch(model, val_loader, device, criterion)
        print(
            f"[{model_name}] epoch {epoch}/{args.epochs} "
            f"train_loss={train_loss:.4f} train_acc={train_acc:.3f} "
            f"val_loss={val_loss:.4f} val_acc={val_acc:.3f}"
        )

        history["train_loss"].append(train_loss)
        history["train_acc"].append(train_acc)
        history["val_loss"].append(val_loss)
        history["val_acc"].append(val_acc)

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            history["best_epoch"] = epoch
            torch.save(model.state_dict(), best_path)
            print(f"Saved best checkpoint (val_acc={val_acc:.3f}): {best_path}")

        if checkpointing and epoch in args.checkpoint_epochs:
            ckpt_path = checkpoint_dir / f"{model_name}_run{run_id}_epoch{epoch}.pt"
            torch.save(model.state_dict(), ckpt_path)
            print(f"Saved checkpoint: {ckpt_path}")

    with open(history_path, "w") as f:
        json.dump(history, f, indent=2)


def load_histories(
        checkpoint_dir: Path,
        model_name: str
) -> list:
    paths = sorted(Path(checkpoint_dir).glob(f"{model_name}_run*_history.json"))
    return [json.loads(p.read_text()) for p in paths]


def discover_model_names(
        checkpoint_dir: Path
) -> list:
    names = set()
    for p in Path(checkpoint_dir).glob("*_run*_history.json"):
        if match := re.match(r"(.+)_run\d+_history\.json", p.name):
            names.add(match.group(1))
    return sorted(names)


def mean_and_ci(
        values: np.ndarray
) -> tuple:
    """ Mean and 95% CI half-width (1.96 * SEM) across axis 0 (runs).

    Args:
        values: Array of shape (n_runs, ...).

    Returns:
        Tuple of (mean, CI half-width), each of shape values.shape[1:].
    """
    mean = values.mean(axis=0)
    if values.shape[0] < 2:
        return mean, np.zeros_like(mean)
    sem = values.std(axis=0, ddof=1) / np.sqrt(values.shape[0])
    return mean, 1.96 * sem


def plot_accuracy_history(
        checkpoint_dir,
        model_names=None
):
    checkpoint_dir = Path(checkpoint_dir)
    model_names = list(model_names or discover_model_names(checkpoint_dir))[::-1]

    fig, axes = plt.subplots(1, len(model_names), figsize=(5 * len(model_names), 4), squeeze=False, sharey=True)

    for ax, model_name in zip(axes[0], model_names):
        histories = load_histories(checkpoint_dir, model_name)
        n_epochs = min(len(h["train_acc"]) for h in histories)
        epochs = np.arange(1, n_epochs + 1)

        for key, color, label in [("train_acc", "tab:blue", "train"), ("val_acc", "tab:orange", "val")]:
            values = np.array([h[key][:n_epochs] for h in histories])
            mean, ci = mean_and_ci(values)
            ax.plot(epochs, mean, color=color, label=label)
            ax.fill_between(epochs, mean - ci, mean + ci, color=color, alpha=0.2)

        ax.set_title(f"{model_name} (n={len(histories)} runs)")
        ax.set_xlabel("epoch")
        ax.set_ylabel("accuracy")
        ax.legend()

    axes[0, 0].set_ylim(bottom=0)

    fig.tight_layout()
    return fig
