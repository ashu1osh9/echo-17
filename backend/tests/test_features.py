import numpy as np
from ml.prepare import stats


def test_feature_statistics():
    row = np.array([[1., 2., 3., 4.], [10., 10., 10., 10.]], dtype=np.float32)
    a = stats(row)
    assert a.shape == (2, 6)
    assert np.allclose(a[:, 0], [2.5, 10])
    assert a[1, 1] == 0


def test_model_input_does_not_include_targets():
    import pandas as pd
    from ml.prepare import FEATURE_COLUMNS, model_features
    frame = pd.DataFrame({name: [1.] for name in FEATURE_COLUMNS})
    for name in ("cycle_id", "cooler_condition", "stable", "valve_condition", "pump", "accumulator"):
        frame[name] = 100
    assert model_features(frame).columns.tolist() == list(FEATURE_COLUMNS)
    assert len(model_features(frame).columns) == 36


def test_bad_alignment_and_sampling_rejected():
    import pytest
    from ml.prepare import validate_sensor, validate_profile
    with pytest.raises(ValueError, match="profile shape"):
        validate_profile(np.zeros((2204, 5)))
    with pytest.raises(ValueError, match="expected shape"):
        validate_sensor("TS1", np.zeros((2204, 60)), 2205)
    with pytest.raises(ValueError, match="expected shape"):
        validate_sensor("TS1", np.zeros((2205, 59)), 2205)


def test_nonfinite_measurements_rejected():
    import pytest
    from ml.prepare import validate_sensor
    with pytest.raises(ValueError, match="non-finite"):
        validate_sensor("TS1", np.full((2, 60), np.nan), 2)


def test_stratified_split_is_deterministic_and_disjoint():
    import pandas as pd
    from ml.train_baseline import split_indices
    frame = pd.DataFrame({"cooler_condition": np.repeat([3, 20, 100], 735)})
    train, test = split_indices(frame)
    train_again, test_again = split_indices(frame)
    assert np.array_equal(train, train_again) and np.array_equal(test, test_again)
    assert len(train) == 1764 and len(test) == 441
    assert not set(train) & set(test)
    assert set(train) | set(test) == set(range(2205))
