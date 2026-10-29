import numpy as np
from ml.prepare import stats


def test_feature_statistics():
    row = np.array([[1., 2., 3., 4.], [10., 10., 10., 10.]], dtype=np.float32)
    a = stats(row)
    assert a.shape == (2, 6)
    assert np.allclose(a[:, 0], [2.5, 10])
    assert a[1, 1] == 0


def test_model_input_does_not_include_targets():
    from pathlib import Path
    source = (Path(__file__).resolve().parents[1] / "ml" / "train_baseline.py").read_text()
    assert '"cooler_condition", "stable"' in source
