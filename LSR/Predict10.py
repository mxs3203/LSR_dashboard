import torch


class Predict10(torch.nn.Module):
    def __init__(self, curve_size):
        super().__init__()

        self.decoder = torch.nn.Sequential(
            torch.nn.Linear(curve_size, 128),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.2),
            torch.nn.Linear(128, 128),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.2),
            torch.nn.Linear(128, 128),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.2),
            torch.nn.Linear(128, 128),
            torch.nn.ReLU(),
            torch.nn.Linear(128, 10)
        )

    def forward(self, x):
        return self.decoder(x)