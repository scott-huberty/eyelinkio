#this is scott huberty's original file
# """Test that an error is raised if SR Research's edfapi is not installed."""


from unittest.mock import patch

import numpy as np
import pytest

from eyelinkio import read_edf
from eyelinkio.utils import _get_test_fnames, requires_edfapi

fnames = _get_test_fnames()
mne = pytest.importorskip('mne')
pandas = pytest.importorskip('pandas')

@requires_edfapi
def test_read_raw():
    """Test reading raw data."""
    for fname in fnames:
        edf_file = read_edf(fname)
        # test repr
        assert repr(edf_file)

        # tests dtypes are parsed correctly that is double only
        assert edf_file['samples'].dtype == np.float64

        if fname.name == "test_raw_binocular.edf":
            # XXX: ideally we should get a binocular file with a calibration
            assert edf_file["info"]["eye"] == "BINOCULAR"
            assert len(edf_file["discrete"]["blinks"]) == 195
            np.testing.assert_equal(edf_file["discrete"]["starts"]["stime"][0], 0.0)
            np.testing.assert_almost_equal(
                edf_file["discrete"]["ends"]["stime"][-1], 199.644
                )

        elif fname.name == "test_2_raw.edf":  # First test file has this property
            for kind in ['saccades', 'fixations', 'blinks']:
                assert edf_file["discrete"][kind][0]['stime'] < 12.0

        elif fname.name == "test_raw.edf":
            want_point_x = np.array([960, 1600, 320, 960, 960])
            want_point_y = np.array([540, 540, 540, 720, 360])
            want_offsets = np.array([0.12, 0.40, 0.12, 0.65, 0.35])
            want_diff_x = np.array([0.3, -10.1, -4.5, -24.3, -7.3])
            want_diff_y = np.array([-4.4, 10.9, 0.1, -2.9, -10.9])

            assert len(edf_file["info"]["calibrations"]) == 1
            cal = edf_file["info"]["calibrations"][0]
            validation = cal["validation"]

            np.testing.assert_allclose(validation["point_x"], want_point_x)
            np.testing.assert_allclose(validation["point_y"], want_point_y)
            np.testing.assert_allclose(validation["offset"], want_offsets)
            np.testing.assert_allclose(validation["diff_x"], want_diff_x)
            np.testing.assert_allclose(validation["diff_y"], want_diff_y)
            assert cal["eye"] == "left"
            assert cal["model"] == "HV5"
            np.testing.assert_equal(cal["onset"], 0.136)
        else:
            continue

        if fname.name == "test_raw.edf" or fname.name == "test_2_raw.edf":
            # the following should be true for both monocular test files
            assert edf_file['times'][0] < 1.0
            assert edf_file["info"]["eye"] == "LEFT_EYE"
            assert edf_file["info"]["ps_units"] == "PUPIL_AREA"


def test_to_pandas():
    """Test converting EDF to pandas DataFrame."""
    fnames = _get_test_fnames() # test_raw.edf
    for fname in fnames:
        edf_file = read_edf(fname)
        dfs = edf_file.to_pandas()
        assert isinstance(dfs, dict)

        if fname.name == "test_raw.edf":
            np.testing.assert_equal(
                dfs["discrete"]["blinks"]["eye"].unique(), "LEFT_EYE"
                )
            assert dfs["discrete"]["messages"]["msg"][0] == "RECCFG CR 1000 2 1 L"

            # calibration
            assert len(dfs["calibrations"]) == 5
            want_offset = np.array([0.12, 0.40, 0.12, 0.65, 0.35])
            np.testing.assert_allclose(dfs["calibrations"]["offset"], want_offset)

        elif fname.name == "test_2_raw.edf":
            np.testing.assert_equal(
                dfs["discrete"]["blinks"]["eye"].unique(), "LEFT_EYE"
                )
            assert dfs["discrete"]["messages"]["msg"][0] == "RECCFG CR 1000 2 1 L"

        elif fname.name == "test_raw_binocular.edf":
            want_eyes = ["LEFT_EYE", "RIGHT_EYE"]
            got_eyes = dfs["discrete"]["blinks"]["eye"].unique()
            np.testing.assert_equal(got_eyes, want_eyes)

        else:
            continue

def test_to_mne():
    """Test converting EDF to MNE."""
    import mne

    fnames = _get_test_fnames()
    for fname in fnames:
        edf_file = read_edf(fname)
        raw, cals = edf_file.to_mne()

        if fname.name == "test_raw.edf":
            assert isinstance(raw, mne.io.RawArray)
            assert raw.info["sfreq"] == edf_file["info"]["sfreq"]

            tz = raw.info["meas_date"].tzinfo
            want_measdate = edf_file["info"]["meas_date"].replace(tzinfo=tz)
            assert raw.info["meas_date"] == want_measdate

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

        elif fname.name == "test_2_raw.edf":
            assert isinstance(raw, mne.io.RawArray)
            assert raw.info["sfreq"] == edf_file["info"]["sfreq"]

            tz = raw.info["meas_date"].tzinfo
            got_measdate = edf_file["info"]["meas_date"].replace(tzinfo=tz)
            want_measdate = raw.info["meas_date"]
            assert want_measdate == got_measdate

            want_ch_names = ["xpos_left", "ypos_left", "ps_left"]
            np.testing.assert_equal(raw.ch_names, want_ch_names)

            want_coil = mne.io.constants.FIFF.FIFFV_COIL_EYETRACK_POS
            want_kind =  mne.io.constants.FIFF.FIFFV_EYETRACK_CH
            assert raw.info["chs"][0]["kind"] == want_kind
            assert raw.info["chs"][0]["coil_type"] == want_coil
            assert raw.info["chs"][0]["loc"][3] == -1
            assert raw.info["chs"][0]["loc"][4] == -1
            assert raw.info["chs"][1]["loc"][4] == 1

        elif fname.name == "test_raw_binocular.edf":
            want_chs = [f"{ch}_{eye}"
                        for ch in ["xpos", "ypos", "ps"]
                        for eye in ["left", "right"]
                        ]
            np.testing.assert_equal(raw.ch_names, want_chs)
        else:
            continue

def test_edfapi_not_installed():
    """Test that an error is raised if SR Research's edfapi is not installed."""
    with patch("eyelinkio.edf.read.has_edfapi", False):
            with pytest.raises(OSError, match="Could not load EDF api"):
                read_edf(fnames[0])
