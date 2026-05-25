from types import SimpleNamespace

import torch

import classifier
from classifier import BertSentimentClassifier


class DummyBert(torch.nn.Module):
    hidden_size = 4

    def __init__(self):
        super().__init__()
        self.dummy_param = torch.nn.Parameter(torch.ones(1))

    @classmethod
    def from_pretrained(cls, *args, **kwargs):
        return cls()

    def forward(self, input_ids, attention_mask):
        batch = input_ids.size(0)
        base = torch.arange(batch * self.hidden_size, dtype=torch.float32).view(batch, self.hidden_size)
        return {"pooler_output": base}


def test_classifier_adds_projection_and_dropout(monkeypatch):
    monkeypatch.setattr(classifier, "BertModel", DummyBert)

    config = SimpleNamespace(
        hidden_size=DummyBert.hidden_size,
        hidden_dropout_prob=0.0,
        num_labels=3,
        option="pretrain",
    )
    model = BertSentimentClassifier(config)

    token_ids = torch.ones(2, 5, dtype=torch.long)
    attention_mask = torch.ones_like(token_ids)

    logits = model(token_ids, attention_mask)
    assert logits.shape == (2, config.num_labels)

    base = torch.arange(2 * DummyBert.hidden_size, dtype=torch.float32).view(2, DummyBert.hidden_size)
    expected = model.proj(base)
    assert torch.allclose(logits, expected)
    assert all(param.requires_grad is False for param in model.bert.parameters())
