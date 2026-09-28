"""Pre-implemented core functions to use for the assignment."""

import csv
import random
from pathlib import Path

import h5py
import numpy as np
import torch
import torchaudio
from torch.utils.data import Dataset

from config import (
    CLIP_DURATION, DATA_DIR, N_MELS, SAMPLE_RATE, SANTORO_LABELS_CSV, SANTORO_SOUNDS_DIR, SNIPPET_DURATION,
)
from models import WaveformModel, UninspiredModel, InspiredModel
from util import load_waveform, yamnet_filename_map


class ESC50Dataset(Dataset):
    """ Loads the ESC-50 sound files and crops a random 1s snippet (SNIPPET_DURATION) out of each 5s recording.

    Returns both the raw waveform snippet and its mel-spectrogram. The random crop changes on every access, acting
    as data augmentation. 1s subselection is performed to match the 1s duration of the Santoro sounds and the Yamnet
    embeddings.

    Args:
        audio_dir: Directory containing the ESC-50 .wav files.
        meta_csv: Path to the ESC-50 metadata CSV (gives filename, fold, and target per clip).
        folds: Fold numbers (1-5) to include.
        sample_rate: Sample rate to resample clips to.
    """

    def __init__(
            self,
            audio_dir: Path,
            meta_csv: Path,
            folds,
            sample_rate: int
    ):
        self.audio_dir = Path(audio_dir)
        self.sample_rate = sample_rate
        self.clip_num_samples = int(sample_rate * CLIP_DURATION)
        self.snippet_num_samples = int(sample_rate * SNIPPET_DURATION)

        with open(meta_csv, newline="") as f:
            rows = list(csv.DictReader(f))
        self.rows = [row for row in rows if int(row["fold"]) in folds]

        self.mel_spectrogram = torchaudio.transforms.MelSpectrogram(sample_rate=sample_rate, n_mels=N_MELS)
        self.to_db = torchaudio.transforms.AmplitudeToDB()

    def __len__(self):
        return len(self.rows)

    def __getitem__(
            self,
            index
    ):
        row = self.rows[index]
        waveform = load_waveform(self.audio_dir / row["filename"], self.sample_rate, self.clip_num_samples)

        start = random.randint(0, self.clip_num_samples - self.snippet_num_samples)
        waveform = waveform[start: start + self.snippet_num_samples]

        spectrogram = self.to_db(self.mel_spectrogram(waveform)).unsqueeze(0)  # (1, n_mels, n_frames)
        label = int(row["target"])

        return waveform, spectrogram, label


class SantoroDataset(Dataset):
    """ Loads all 288 sounds from the Santoro et al. fMRI dataset and pairs them with their betas.

    Uses config.SAMPLE_RATE, the same rate ESC50Dataset and WaveformModel use, so a trained WaveformModel can be
    run on these sounds directly.
    """

    BETAS_KEYS = {"test": "BetasTest", "train": "BetasTrain"}
    SOUND_KEYS = {"test": "testSounds", "train": "trainSounds"}

    def __init__(self):
        self.sounds_dir = SANTORO_SOUNDS_DIR
        self.sample_rate = SAMPLE_RATE
        self.target_num_samples = int(SAMPLE_RATE * SNIPPET_DURATION)

        with open(SANTORO_LABELS_CSV, newline="") as f:
            rows = list(csv.reader(f, delimiter=";"))
        self.categories = [row[0] for row in rows]
        self.filenames = [row[-1] for row in rows]

        sub_indices, sub_betas = zip(*(self._load_split(s) for s in self.BETAS_KEYS))
        order = np.argsort(np.concatenate(sub_indices))
        betas = np.concatenate(sub_betas, axis=1)[:, order]  # now in ascending sound-index order

        self.brain_responses = torch.from_numpy(betas.T).float()  # (n_sounds, n_voxels)

        self.mel_spectrogram = torchaudio.transforms.MelSpectrogram(sample_rate=SAMPLE_RATE, n_mels=N_MELS)
        self.to_db = torchaudio.transforms.AmplitudeToDB()

    def _load_split(
            self,
            split: str
    ):
        with h5py.File(DATA_DIR / f"{split}_sound_keys.mat", "r") as f:
            indices = np.sort(f[self.SOUND_KEYS[split]][:].flatten().astype(int))

        with h5py.File(DATA_DIR / f"stg_betas_{split}.mat", "r") as f:
            betas = np.array(f[self.BETAS_KEYS[split]])  # (n_voxels, n_sounds)

        return indices, betas

    def __len__(self):
        return len(self.filenames)

    def __getitem__(
            self,
            index
    ):
        waveform = load_waveform(self.sounds_dir / self.filenames[index], self.sample_rate, self.target_num_samples)
        spectrogram = self.to_db(self.mel_spectrogram(waveform)).unsqueeze(0)  # (1, n_mels, n_frames)
        brain_response = self.brain_responses[index]
        category = self.categories[index]

        return waveform, spectrogram, brain_response, category


def load_yamnet_activations(
        layer: str = None
) -> dict:
    """ Reads the YAMNet activations and returns a {layer_name: (288, n_features) array}, one row per sound in the
    same order as SantoroDataset, averaged over YAMNet's 2 temporal frames per sound.

    Args:
        layer: Specific layer to return. Leave out to get every layer.

    Returns:
        Dict mapping layer name(s) to a (288, n_features) array.
    """
    with open(SANTORO_LABELS_CSV, newline="") as f:
        filenames = [row[-1] for row in csv.reader(f, delimiter=";")]

    mapping = yamnet_filename_map()
    layers = [f"layer{i:02d}relu" for i in range(1, 15)] + ["embedding"] if layer is None else [layer]
    activations = {name: [] for name in layers}
    for filename in filenames:
        with h5py.File(mapping[filename], "r") as f:
            for name in layers:
                activations[name].append(np.asarray(f[name]).mean(axis=0).reshape(-1))

    return {name: np.stack(vectors) for name, vectors in activations.items()}


def extract_activations(
        dataloader,
        model
) -> dict:
    """ Runs `model` over every batch in `dataloader` and returns a dict mapping each trainable layer's name to its
    activations across all samples, as a tensor of shape (n_samples, *layer_output_shape).

    Args:
        dataloader: Yields batches to run through `model`.
        model: Model to extract layer activations from.

    Returns:
        Dict mapping each trainable layer's name to its activations, shape (n_samples, *layer_output_shape).
    """
    device = next(model.parameters()).device
    model.eval()

    def is_activation(
            module
    ):
        return type(module).__module__ == "torch.nn.modules.activation"

    trainable_names = [name for name, m in model.named_modules() if list(m.parameters(recurse=False))]
    trainable_name_set = set(trainable_names)
    tracked = {name: m for name, m in model.named_modules() if name in trainable_name_set or is_activation(m)}
    activations = {name: [] for name in trainable_names}  # preserves the model's own layer order

    call_order = []

    def make_hook(name):
        def hook(module, inputs, output):
            output = output[0] if isinstance(output, tuple) else output
            call_order.append((name, output))
        return hook

    handles = [module.register_forward_hook(make_hook(name)) for name, module in tracked.items()]

    with torch.no_grad():
        for batch in dataloader:
            inputs = batch[0] if isinstance(model, WaveformModel) else batch[1]
            call_order.clear()
            model(inputs.to(device))

            for i, (name, output) in enumerate(call_order):
                if name not in trainable_name_set:
                    continue
                if i + 1 < len(call_order) and call_order[i + 1][0] not in trainable_name_set:
                    output = call_order[i + 1][1]  # the following activation's output
                activations[name].append(output.detach().cpu())

    for handle in handles:
        handle.remove()

    return {name: torch.cat(chunks, dim=0) for name, chunks in activations.items()}


MODEL_CLASSES = {
    "waveform": WaveformModel,
    "uninspired": UninspiredModel,
    "inspired": InspiredModel,
}
