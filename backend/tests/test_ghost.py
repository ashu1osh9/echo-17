"""Small isolated fixtures verify reference selection; never used for app demonstrations."""
import pandas as pd
from app.services import ghost


def test_reference_only_from_training_healthy_cooler(monkeypatch):
    frame = pd.DataFrame(
        {"PS1_mean": [9.0, 9.1, 1.0, 8.8], "PS1_std": [1.0, 1.0, 1.0, 1.0],
         "cooler_condition": [3, 100, 100, 100], "stable": [0, 0, 0, 1]},
        index=[1, 2, 3, 4],
    )
    monkeypatch.setattr(ghost, "features", lambda: frame)
    monkeypatch.setattr(ghost, "training_ids", lambda: [2, 3, 4])
    monkeypatch.setattr(ghost, "validate_cycle", lambda _: None)
    ref_id, dist = ghost.select_reference(1)
    assert ref_id == 2
    assert dist >= 0
