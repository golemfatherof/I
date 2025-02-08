import torch
from torch import nn
import pytorch_lightning as pl

class LitModel(pl.LightningModule):
    def __init__(self):
        super().__init__()
        self.layer = nn.Linear(32, 2)

    def forward(self, x):
        return self.layer(x)

    def training_step(self, batch, batch_idx):
        loss = nn.CrossEntropyLoss()(batch, batch)
        return loss

    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=1e-3)
