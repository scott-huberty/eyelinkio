import numpy as np
import pytest

from eyelinkio.io import read_edf
from eyelinkio.utils import _get_test_fnames
from eyelinkio.utils.check import requires_edfapi

fnames = _get_test_fnames()

@requires_edfapi
def test_read_raw():
    """Test reading raw data."""
    for fname in fnames:
        edf_file = read_edf(fname)
        # test repr
        assert repr(edf_file)

        # tests dtypes are parsed correctly that is double only
        assert edf_file['samples'].dtype == np.float64

        if fname.name == "test_2_raw.edf":  # First test file has this property
            for kind in ['saccades', 'fixations', 'blinks']:
                assert edf_file["discrete"][kind][0]['stime'] < 12.0
        assert edf_file['times'][0] < 1.0
        assert edf_file["info"]["eye"] == "LEFT_EYE"
        assert edf_file["info"]["ps_units"] == "PUPIL_AREA"

pytest.importorskip('pandas')
def test_to_pandas():
    """Test converting EDF to pandas DataFrame."""
    fname = _get_test_fnames()[1] # test_raw.edf
    edf_file = read_edf(fname)
    dfs = edf_file.to_pandas()
    assert isinstance(dfs, dict)
    np.testing.assert_equal(dfs["discrete"]["blinks"]["eye"].unique(), "LEFT_EYE")
    assert dfs["discrete"]["messages"]["msg"][0] == "RECCFG CR 1000 2 1 L"

pytest.importorskip('mne')
def test_to_mne():
    """Test converting EDF to MNE."""
    import mne

    fname = _get_test_fnames()[1] # test_raw.edf
    edf_file = read_edf(fname)
    raw, cals = edf_file.to_mne()
    assert isinstance(raw, mne.io.RawArray)
    assert raw.info["sfreq"] == edf_file["info"]["sfreq"]
    tz = raw.info["meas_date"].tzinfo
    assert raw.info["meas_date"] == edf_file["info"]["meas_date"].replace(tzinfo=tz)
    # annotations
    assert len(raw.annotations) == 148
    assert raw.annotations[92]["description"] == "BAD_blink"
    np.testing.assert_allclose(raw.annotations[92]["onset"], 11.298)
    np.testing.assert_allclose(raw.annotations[92]["duration"], .089)
    ch_names = ('xpos_left', 'ypos_left', 'ps_left')
    np.testing.assert_equal(raw.annotations[92]["ch_names"], ch_names)
    np.testing.assert_allclose(raw.annotations[0]["onset"], 0.0)
    # calibration
    # these values were taken from the ASCII file (ground truth)
    point_x = np.array([960, 1600, 320, 960, 960])
    point_y = np.array([540, 540, 540, 720, 360])
    offsets = np.array([0.12, 0.40, 0.12, 0.65, 0.35])
    diff_x = np.array([0.3, -10.1, -4.5, -24.3, -7.3])
    diff_y = np.array([-4.4, 10.9, 0.1, -2.9, -10.9])
    want_positions = np.array([point_x, point_y]).T
    want_gaze = np.array([point_x + diff_x, point_y + diff_y]).T
    want_avg_error = np.mean(offsets)
    want_max_error = np.max(offsets)
    cal = cals[0]
    assert cal["eye"] == "left"
    np.testing.assert_allclose(cal["positions"], want_positions)
    np.testing.assert_allclose(cal["gaze"], want_gaze)
    np.testing.assert_allclose(cal["offsets"], offsets)
    np.testing.assert_allclose(cal["avg_error"], want_avg_error)
    np.testing.assert_allclose(cal["max_error"], want_max_error)
