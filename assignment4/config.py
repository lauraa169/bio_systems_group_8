from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"

# ESC-50 (training data for Part II)
ESC50_AUDIO_DIR = "<your-path-to-esc50>/audio"
ESC50_META_CSV = "<your-path-to-esc50>/meta/esc50.csv"
CLIP_DURATION = 5.0
NUM_CLASSES = 50

# Santoro natural-sounds fMRI dataset (brain data for Part I)
SANTORO_SOUNDS_DIR = DATA_DIR / "santoro_sounds"
SANTORO_LABELS_CSV = SANTORO_SOUNDS_DIR / "Labels_288Sounds_ObjectSoundDescription.csv"

# YAMNet embeddings
YAMNET_DIR = DATA_DIR / "yamnet_embeddings"

# shared model/data constants
N_MELS = 64
SNIPPET_DURATION = 1.0

# default training hyperparameters (train.py CLI defaults)
CHECKPOINT_DIR = "models"
EPOCHS = 10
BATCH_SIZE = 16
LEARNING_RATE = 1e-3
SAMPLE_RATE = 8000
VAL_FOLD = 5
NUM_WORKERS = 0
N_MODELS = 1
