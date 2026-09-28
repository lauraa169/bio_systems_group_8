"""Train WaveformModel, UninspiredModel, and InspiredModel on ESC-50 environmental sound classification."""

import argparse

from torch.utils.data import DataLoader

import config
from core import ESC50Dataset, MODEL_CLASSES
from util import confirm_device, resolve_device, train_model


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audio-dir", default=config.ESC50_AUDIO_DIR)
    parser.add_argument("--meta-csv", default=config.ESC50_META_CSV)
    parser.add_argument("--checkpoint-dir", default=config.CHECKPOINT_DIR)
    parser.add_argument("--epochs", type=int, default=config.EPOCHS)
    parser.add_argument("--checkpoint-epochs", type=int, nargs="*", default=[],
                         help="epochs to save a checkpoint at (also saves the untrained epoch-0 weights); "
                              "checkpointing is off by default, e.g. pass '5 10' to enable it")
    parser.add_argument("--batch-size", type=int, default=config.BATCH_SIZE)
    parser.add_argument("--lr", type=float, default=config.LEARNING_RATE)
    parser.add_argument("--val-fold", type=int, default=config.VAL_FOLD, help="ESC-50 fold (1-5) held out for validation")
    parser.add_argument("--num-workers", type=int, default=config.NUM_WORKERS)
    parser.add_argument("--models", nargs="+", default=list(MODEL_CLASSES), choices=list(MODEL_CLASSES))
    parser.add_argument("--n-models", type=int, default=config.N_MODELS, help="how many independently trained models to train per requested model type")
    parser.add_argument("--device", default=None, help="cuda, mps, or cpu; auto-detected if omitted")
    args = parser.parse_args()

    device = resolve_device(args.device)
    confirm_device(device)

    train_folds = [fold for fold in range(1, 6) if fold != args.val_fold]
    train_set = ESC50Dataset(args.audio_dir, args.meta_csv, folds=train_folds, sample_rate=config.SAMPLE_RATE)
    val_set = ESC50Dataset(args.audio_dir, args.meta_csv, folds=[args.val_fold], sample_rate=config.SAMPLE_RATE)
    print(f"train clips: {len(train_set)}, val clips (fold {args.val_fold}): {len(val_set)}")

    train_loader = DataLoader(train_set, batch_size=args.batch_size, shuffle=True, num_workers=args.num_workers)
    val_loader = DataLoader(val_set, batch_size=args.batch_size, shuffle=False, num_workers=args.num_workers)

    for model_name in args.models:
        model_class = MODEL_CLASSES[model_name]
        for _ in range(args.n_models):
            model = model_class(num_classes=config.NUM_CLASSES)
            train_model(model_name, model, train_loader, val_loader, args, device)


if __name__ == "__main__":
    main()
