import torch


class Predict10(torch.nn.Module):
    def __init__(self, curve_size):
        super().__init__()

        self.decoder = torch.nn.Sequential(
            torch.nn.Linear(curve_size, 64),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.19),
            torch.nn.Linear(64, 64),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.19),
            torch.nn.Linear(64, 64),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.19),
            torch.nn.Linear(64, 64),
            torch.nn.ReLU(),
            torch.nn.Linear(64, 10)
        )

    def forward(self, x):
        return self.decoder(x)

