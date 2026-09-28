"""Pre-implemented models of sound event recognition."""

import torch

from config import SAMPLE_RATE, SNIPPET_DURATION


class WaveformModel(torch.nn.Module):
    """ Super simple model that operates directly on raw waveforms: 5 fully connected layers with tanh activations,
    followed by a linear classifier returning logits.

    Args:
        num_classes: Number of output classes.
    """

    def __init__(
            self,
            num_classes: int
    ):
        super().__init__()
        input_length = int(SAMPLE_RATE * SNIPPET_DURATION)
        hidden_sizes = (1024, 512, 256, 128, 64)

        self.flatten = torch.nn.Flatten()

        sizes = [input_length, *hidden_sizes]
        self.hidden_layers = torch.nn.ModuleList([
            torch.nn.Linear(sizes[i], sizes[i + 1]) for i in range(len(hidden_sizes))
        ])
        self.activation = torch.nn.Tanh()

        self.classifier = torch.nn.Linear(hidden_sizes[-1], num_classes)

    def forward(
            self,
            waveform: torch.Tensor
    ) -> torch.Tensor:
        x = self.flatten(waveform)
        for layer in self.hidden_layers:
            x = self.activation(layer(x))
        return self.classifier(x)


class UninspiredModel(torch.nn.Module):
    """ More complex but still uninspired model that now operates on spectrograms: 3 convolutional layers with
    tanh activations, followed by 2 fully connected layers and a linear classifier returning logits.

    Args:
        num_classes: Number of output classes.
    """

    def __init__(
            self,
            num_classes: int
    ):
        super().__init__()
        conv_channels = (1, 16, 32, 64)
        fc_sizes = (64, 128, 64)

        self.conv_layers = torch.nn.ModuleList([
            torch.nn.Conv2d(conv_channels[i], conv_channels[i + 1], kernel_size=3, padding=1)
            for i in range(len(conv_channels) - 1)
        ])
        self.pool = torch.nn.MaxPool2d(2)
        self.activation = torch.nn.Tanh()

        self.fc_layers = torch.nn.ModuleList([
            torch.nn.Linear(fc_sizes[i], fc_sizes[i + 1]) for i in range(len(fc_sizes) - 1)
        ])

        self.classifier = torch.nn.Linear(fc_sizes[-1], num_classes)

    def forward(
            self,
            spectrogram: torch.Tensor
    ) -> torch.Tensor:
        x = spectrogram
        for conv in self.conv_layers:
            x = self.pool(self.activation(conv(x)))
        x = x.mean(dim=(-2, -1))
        for fc in self.fc_layers:
            x = self.activation(fc(x))
        return self.classifier(x)


class InspiredModel(torch.nn.Module):
    """ The most complex model, operating on spectrograms: 3 convolutional layers with ReLU6 activations extract local
    time-frequency features, 2 stacked recurrent (GRU) layers integrate information over time, and a linear classifier
    returns logits. Its conv -> recurrent structure loosely mirrors the auditory system's hierarchy of local
    spectrotemporal filtering followed by temporal integration.

    Args:
        num_classes: Number of output classes.
    """

    def __init__(
            self,
            num_classes: int
    ):
        super().__init__()
        conv_channels = (1, 16, 32, 64)
        rnn_hidden_size = 128

        self.conv_layers = torch.nn.ModuleList([
            torch.nn.Conv2d(conv_channels[i], conv_channels[i + 1], kernel_size=3, padding=1)
            for i in range(len(conv_channels) - 1)
        ])
        self.pool = torch.nn.MaxPool2d(2)
        self.activation = torch.nn.ReLU6()

        self.rnn = torch.nn.GRU(
            input_size=conv_channels[-1], hidden_size=rnn_hidden_size, num_layers=2, batch_first=True,
        )

        self.classifier = torch.nn.Linear(rnn_hidden_size, num_classes)

    def forward(
            self,
            spectrogram: torch.Tensor
    ) -> torch.Tensor:
        """ Runs the model forward.

        Args:
            spectrogram: Tensor of shape (batch, 1, n_freq, n_time).

        Returns:
            Logits of shape (batch, num_classes).
        """
        x = spectrogram
        for conv in self.conv_layers:
            x = self.pool(self.activation(conv(x)))

        x = x.mean(dim=2).transpose(1, 2)

        _, hidden = self.rnn(x)
        last_hidden = hidden[-1]

        return self.classifier(last_hidden)
