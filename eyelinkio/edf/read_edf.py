"""Functions for reading Eyelink EDF Files."""

import ctypes as ct
import re
import warnings
from datetime import datetime
from functools import partial
from os import path as op
from pathlib import Path

import numpy as np

try:
    from ._edf2py import (
        edf_close_file,
        edf_get_float_data,
        edf_get_next_data,
        edf_get_preamble_text,
        edf_get_preamble_text_length,
        edf_get_version,
        edf_open_file,
    )

    has_edfapi = True
    why_not = None
except OSError as exp:
    (
        edf_open_file,
        edf_close_file,
        edf_get_next_data,
        edf_get_preamble_text,
        edf_get_preamble_text_length,
        edf_get_version,
        edf_get_float_data,
    ) = [None] * 8
    has_edfapi = False
    why_not = str(exp)

from . import _defines as defines
from ._defines import event_constants

_MAX_MSG_LEN = 260  # maxmimum message length we'll need to store


def read_edf(fname):
    """Read an EyeLink EDF file.

    Parameters
    ----------
    fname : path-like
        The name of the EDF file.

    Returns
    -------
    edf : EDF
        An instance of EDF:  The EyeLink data represented in Python.
    """
    return EDF(fname)


class EDF(dict):
    """Represent EyeLink EDF files in Python.

    This class is a subclass of :class:`dict`, and so can be indexed like a
    dictionary. To see the available keys, use the ``keys()`` method.

    Parameters
    ----------
    fname : str
        The name of the EDF file.
    """

    def __init__(self, fname):
        if not has_edfapi:
            raise OSError("Could not load EDF api: %s" % why_not)
        info, discrete, times, samples = _read_raw_edf(fname)
        self.info = info
        self.info["filename"] = Path(fname).name
        self.discrete = discrete
        self._times = times
        self._samples = samples
        super().__init__(
            info=info, discrete=discrete, times=times, samples=samples
        )

    def __repr__(self):
        """Return a summary of the EDF File."""
        return (
            f"<EDF | {self['info']['filename']}> \n"
            f"  Version: {self['info']['version']} \n"
            f"  Eye: {self['info']['eye']} \n"
            f"  Pupil unit: {self['info']['ps_units']} \n"
            f"  Sampling frequency: {self['info']['sfreq']} Hz \n"
            f"  Calibrations: {len(self['info']['calibrations'])} \n"
            f"  Length: {len(self['times']) / self['info']['sfreq']} seconds \n"
        )

    def to_pandas(self):
        """Convert an EDF file to a pandas DataFrame.

        Returns
        -------
        df_samples : dict of DataFrame
            A dictionary of :class:`~pandas.DataFrame`'s, containing the samples,
            blinks, saccades, fixations, messages, and calibrations.
        """
        from ..utils import to_pandas
        return to_pandas(self)

    def to_mne(self):
        """Create an MNE Raw object from the EDF object.

        Returns
        -------
        raw : RawEyelink
            An instance of Raw.
        calibrations : list of Calibration
            A list of Calibration objects.
        """
        from ..utils import to_mne
        return to_mne(self)

class _edf_open:
    """Context manager for opening EDF files."""

    def __init__(self, fname):
        self.fname = op.normpath(op.abspath(fname).encode("ASCII"))
        self.fid = None

    def __enter__(self):
        error_code = ct.c_int(1)
        self.fid = edf_open_file(self.fname, 2, 1, 1, ct.byref(error_code))
        if self.fid is None or error_code.value != 0:
            raise OSError(
                'Could not open file "%s": (%s, %s)'
                % (self.fname, self.fid, error_code.value)
            )
        return self.fid

    def __exit__(self, type_, value, traceback):
        if self.fid is not None:
            result = edf_close_file(self.fid)
            if result != 0:
                raise OSError('File "%s" could not be closed' % self.fname)


_ets2pp = dict(
    SAMPLE_TYPE="sample",
    ENDFIX="fixations",
    ENDSACC="saccades",
    ENDBLINK="blinks",
    BUTTONEVENT="buttons",
    INPUTEVENT="inputs",
    MESSAGEEVENT="messages",
)


def _read_raw_edf(fname):
    """Read data from raw EDF file into pyeparse format."""
    if not op.isfile(fname):
        raise OSError('File "%s" does not exist' % fname)

    #
    # First pass: get the number of each type of sample
    #
    n_samps = dict()
    offsets = dict()
    for key in _ets2pp.values():
        n_samps[key] = 0
        offsets[key] = 0
    with _edf_open(fname) as edf:
        etype = None
        while etype != event_constants.get("NO_PENDING_ITEMS"):
            etype = edf_get_next_data(edf)
            if etype not in event_constants:
                raise RuntimeError("unknown type %s" % event_constants[etype])
            ets = event_constants[etype]
            if ets in _ets2pp:
                n_samps[_ets2pp[ets]] += 1

    #
    # Now let's actually read in the data
    #
    with _edf_open(fname) as edf:
        info = _parse_preamble(edf)
        etype = None
        res = dict(
            info=info,
            samples=None,
            n_samps=n_samps,
            offsets=offsets,
            edf_fields=dict(messages=["stime", "msg"]),
            discrete=dict(),
        )
        # XXX: pyeparse represented messages as byte strings.
        # XXX: Maybe we should use regular python strings?
        dtype = [("stime", np.float64), ("msg", "|S%s" % _MAX_MSG_LEN)]
        res["discrete"]["messages"] = np.empty((n_samps["messages"]), dtype=dtype)
        res["eye_idx"] = None  # in case we get input/button before START
        while etype != event_constants.get("NO_PENDING_ITEMS"):
            etype = edf_get_next_data(edf)
            if etype not in event_constants:
                raise RuntimeError("unknown type %s" % event_constants[etype])
            ets = event_constants[etype]
            _element_handlers[ets](edf, res)
        _element_handlers["VERSION"](res)

    #
    # Put info and discrete into correct output format
    #
    discrete = res["discrete"]
    info = res["info"]
    event_types = ("saccades", "fixations", "blinks", "buttons", "inputs", "messages")
    info["sample_fields"] = info["sample_fields"][1:]  # omit time

    #
    # fix sample times
    #
    data = res["samples"][1:]
    data[data >= 100000000.0 - 1] = np.nan
    orig_times = res["samples"][0]  # original times
    assert np.array_equal(orig_times, np.sort(orig_times))
    times = np.arange(len(orig_times), dtype=np.float64) / info["sfreq"]
    for key in event_types:
        if key not in discrete:
            continue
        for sub_key in ("stime", "etime"):
            if sub_key in discrete[key].dtype.names:
                _adjust_time(discrete[key][sub_key], orig_times, times)

    _extract_calibration(info, discrete["messages"])

    # now we correct our time offsets
    return info, discrete, times, data


def _adjust_time(x, orig_times, times):
    """Adjust time, inplace."""
    x[:] = np.interp(x, orig_times, times)


def _extract_calibration(info, messages):
    """Extract calibration from messages."""
    lines = []
    stimes = []
    for this_msg in messages:
        msg = this_msg["msg"].decode("ASCII")
        if msg.startswith("!CAL") or msg.startswith("VALIDATE"):
            lines.append(msg)
            stimes.append(this_msg["stime"])
        if msg.startswith("GAZE_COORDS"):
            coords = msg.split()[-4:]
            coords = [int(round(float(c))) for c in coords]
            info["screen_coords"] = np.array(
                [coords[2] - coords[0] + 1, coords[3] - coords[1] + 1], int
            )
    calibrations = list()
    keys = ["point_x", "point_y", "offset", "diff_x", "diff_y"]
    li = 0
    while li < len(lines):
        line = lines[li]
        if "!CAL VALIDATION " in line and "ABORTED" not in line:
            this_calibration = dict()
            this_eye = re.search(r'\b(LEFT|RIGHT)\b', line)
            if not this_eye:
                raise ValueError(f"Could not find eye in calibration line: {line}")
            this_eye = this_eye.group(0)

            onset = stimes[li]

            cal_kind = line.split("!CAL VALIDATION ")[1].split()[0]
            n_points = int([c for c in cal_kind if c.isdigit()][0])
            this_validation = []
            ni = 0
            while len(this_validation) < n_points:
                ni += 1
                if li + ni >= len(lines):
                    break

                subline = lines[li + ni]
                if "!CAL" in subline:
                    continue
                eye = re.search(r'\b(LEFT|RIGHT)\b', subline)
                if not eye:
                    raise ValueError(f"Can't find eye in calibration line: {subline}")
                eye = eye.group(0)

                if eye != this_eye:
                    continue

                subline = subline.split()
                xy = subline[-6].split(",")
                xy_diff = subline[-2].split(",")
                vals = [
                    float(v)
                    for v in [xy[0], xy[1], subline[-4], xy_diff[0], xy_diff[1]]
                ]
                this_validation.append(vals)

            this_validation = np.array(this_validation)
            dtype = [(key, "f8") for key in keys]
            out = np.empty(len(this_validation), dtype=dtype)
            for key, data in zip(keys, this_validation.T):
                out[key] = data
            # Now add all this information to the calibration
            this_calibration["onset"] = np.round(onset, 3)
            this_calibration["eye"] = this_eye.lower()
            this_calibration["validation"] = out
            this_calibration["model"] = cal_kind
            calibrations.append(this_calibration)
        li += 1
    info["calibrations"] = calibrations


def _extract_sys_info(line):
    """Aux function for preprocessing sys info lines."""
    return line[line.find(":") :].strip(": \r\n")


def _parse_preamble(edf):
    tlen = edf_get_preamble_text_length(edf)
    txt = ct.create_string_buffer(tlen)
    edf_get_preamble_text(edf, txt, tlen + 1)
    preamble_lines = txt.value.decode("ASCII").split("\n")
    info = dict()
    for line in preamble_lines:
        if "!MODE" in line:
            line = line.split()
            info["eye"], info["sfreq"] = line[-1], float(line[-4])
        elif "DATE:" in line:
            line = _extract_sys_info(line).strip()
            fmt = "%a %b  %d %H:%M:%S %Y"
            info["meas_date"] = datetime.strptime(line, fmt)
        elif "VERSION:" in line:
            info["version"] = _extract_sys_info(line)
        elif "CAMERA:" in line:
            info["camera"] = _extract_sys_info(line)
        elif "SERIAL NUMBER:" in line:
            info["serial"] = _extract_sys_info(line)
        elif "CAMERA_CONFIG:" in line:
            info["camera_config"] = _extract_sys_info(line)
    return info


def _to_list(element, keys, idx):
    """Return a list of particular fields of an EyeLink data element."""
    out = list()
    for k in keys:
        v = getattr(element, k)
        if hasattr(v, "_length_"):
            if idx == 2:
                out.extend([v[i] for i in range(v._length_)]) # v[:2]
            else:
                out.append(v[idx])
        else:
            out.append(v)
    return out


def _sample_fields_available(sflags):
    """Indicate which fields are available in a sample.

    Returns a dict where the keys indicate fields (or field groups) of a
    sample; the value for each indicates if the field has been populated
    with data and can be considered as useful information.
    """
    return dict(
        time=bool(sflags & defines.SAMPLE_TIMESTAMP),  # sample time
        gx=bool(sflags & defines.SAMPLE_GAZEXY),  # gaze X position
        gy=bool(sflags & defines.SAMPLE_GAZEXY),  # gaze Y position
        pa=bool(sflags & defines.SAMPLE_PUPILSIZE),  # pupil size
        left=bool(sflags & defines.SAMPLE_LEFT),  # left eye data
        right=bool(sflags & defines.SAMPLE_RIGHT),  # right eye data
        pupilxy=bool(sflags & defines.SAMPLE_PUPILXY),  # raw eye position
        hrefxy=bool(sflags & defines.SAMPLE_HREFXY),  # href eye position
        gazeres=bool(sflags & defines.SAMPLE_GAZERES),  # x,y pixels per deg
        status=bool(sflags & defines.SAMPLE_STATUS),  # sample status
        inputs=bool(sflags & defines.SAMPLE_INPUTS),  # sample inputs
        button=bool(sflags & defines.SAMPLE_BUTTONS),  # sample buttons
        headpos=bool(sflags & defines.SAMPLE_HEADPOS),  # sample head pos
        # if this flag is set for the sample add .5ms to the sample time
        addoffset=bool(sflags & defines.SAMPLE_ADD_OFFSET),
        # reserved variable-length tagged
        tagged=bool(sflags & defines.SAMPLE_TAGGED),
        # user-defineabe variable-length tagged
        utagged=bool(sflags & defines.SAMPLE_UTAGGED),
    )


'''
def _event_fields_available(eflags):
    """
    Returns a dict where the keys indicate fields (or field groups) of an
    EDF event; the value for each indicates if the field has been populated
    with data and can be considered as useful information.
    """
    return dict(
        endtime=bool(eflags & defines.READ_ENDTIME),  # end time
        gres=bool(eflags & defines.READ_GRES),  # gaze resolution xy
        size=bool(eflags & defines.READ_SIZE),  # pupil size
        vel=bool(eflags & defines.READ_VEL),  # velocity (avg, peak)
        status=bool(eflags & defines.READ_STATUS),  # status (error word)
        beg=bool(eflags & defines.READ_BEG),  # start data for vel,size,gres
        end=bool(eflags & defines.READ_END),  # end data for vel,size,gres
        avg=bool(eflags & defines.READ_AVG),  # avg pupil size, velocity
        pupilxy=bool(eflags & defines.READ_PUPILXY),  # position eye data
        hrefxy=bool(eflags & defines.READ_HREFXY),
        gazexy=bool(eflags & defines.READ_GAZEXY),
        begpos=bool(eflags & defines.READ_BEGPOS),
        endpos=bool(eflags & defines.READ_ENDPOS),
        avgpos=bool(eflags & defines.READ_AVGPOS),
    )
'''


_pp2el = dict(
    eye="eye",
    time="time",
    stime="sttime",
    etime="entime",
    xpos="gx",
    ypos="gy",
    sxp="gstx",
    syp="gsty",
    exp="genx",
    eyp="geny",
    axp="gavx",
    ayp="gavy",
    pv="pvel",
    ps="pa",
    aps="avg",
    buttons="buttons",
    input="input",
)
_el2pp = dict()
for key, val in _pp2el.items():
    _el2pp[val] = key


#
# EDF File Handlers
#


def _handle_recording_info(edf, res):
    """RECORDING_INFO."""
    info = res["info"]
    e = edf_get_float_data(edf).contents.rec
    if e.state == 0:  # recording stopped
        return
    if "sfreq" in info:
        assert e.sample_rate == info["sfreq"]
        assert defines.eye_constants[e.eye -1] == info["eye"]
        x = str(defines.pupil_constants[e.pupil_type])
        assert x == info["ps_units"]
        return
    info["sfreq"] = e.sample_rate
    info["ps_units"] = defines.pupil_constants[e.pupil_type]
    # TODO: edfapi eye constants are 1-based, ours are 0-based. Fix this in _defines?
    info["eye"] = defines.eye_constants[e.eye -1]
    res["eye_idx"] = e.eye - 1 # This should be 0: left, 1: right, 2: binocular

    # Figure out sample flags
    sflags = _sample_fields_available(e.sflags)
    want_edf_fields = ["time", "gx", "gy", "pa"]  # XXX Expand?
    have_edf_fields = [field for field in want_edf_fields if sflags[field]]
    res["edf_sample_fields"] = have_edf_fields
    # Figure out the number of columns needed for the samples array
    n_cols = _setup_n_cols(res)
    sample_fld = _setup_col_names(res)
    res["info"]["sample_fields"] = sample_fld
    res["samples"] = np.empty((n_cols, res["n_samps"]["sample"]), np.float64)


def _setup_n_cols(res):
    """Figure out the number of columns needed for the samples array."""
    # list the edf fields that will double for binocular data
    check_fields = ["gx", "gy", "pa"] # XXX: Expand?
    # find out if we have binocular data
    if res["eye_idx"] == 2:
        # find out if we have any of the fields that will double
        n_cols = len(res["edf_sample_fields"])
        for field in check_fields:
            if field in res["edf_sample_fields"]:
                n_cols += 1
    else:
        # monocular data
        n_cols = len(res["edf_sample_fields"])
    return n_cols

def _setup_col_names(res):
    """Figure out the column names for the samples array."""
    sample_fld = [_el2pp[field] for field in res["edf_sample_fields"]]
    # for monocular data, its simple
    if res["eye_idx"] < 2:
       return sample_fld
    else:
        # for binocular data, we need to double up on some fields
        new_sample_fld = []
        for field in sample_fld:
            if field in ["xpos", "ypos", "ps"]: # XXX: Expand?
                new_sample_fld.append(f"{field}_left")
                new_sample_fld.append(f"{field}_right")
            else:
                new_sample_fld.append(field)
        return new_sample_fld


def _handle_sample(edf, res):
    """SAMPLE_TYPE."""
    e = edf_get_float_data(edf).contents.fs
    off = res["offsets"]["sample"]
    res["samples"][:, off] = _to_list(e, res["edf_sample_fields"], res["eye_idx"])
    res["offsets"]["sample"] += 1


def _handle_message(edf, res):
    """MESSAGEEVENT."""
    e = edf_get_float_data(edf).contents.fe
    msg = ct.string_at(ct.byref(e.message[0]), e.message.contents.len + 1)[2:]
    msg = msg.decode("UTF-8")
    msg = "".join([i if ord(i) < 128 else "" for i in msg])
    if len(msg) > _MAX_MSG_LEN:
        warnings.warn("Message truncated to %s characters:\n%s" % (_MAX_MSG_LEN, msg))
    off = res["offsets"]["messages"]
    res["discrete"]["messages"]["stime"][off] = e.sttime
    res["discrete"]["messages"]["msg"][off] = msg[:_MAX_MSG_LEN]
    res["offsets"]["messages"] += 1


def _handle_end(edf, res, name):
    """ENDSACC, ENDFIX, ENDBLINK, BUTTONS, INPUT."""
    if name not in res["discrete"]:
        # XXX This should be changed to support given fields
        if name == "saccades":
            f = ["eye", "sttime", "entime", "gstx", "gsty", "genx", "geny", "pvel"]
        elif name == "fixations":
            f = ["eye", "sttime", "entime", "gavx", "gavy"]
        elif name == "blinks":
            f = ["eye", "sttime", "entime"]
        elif name == "buttons":
            f = ["sttime", "buttons"]
        elif name == "inputs":
            f = ["sttime", "input"]
        else:
            raise KeyError("Unknown name %s" % name)
        res["edf_fields"][name] = f
        our_names = [_el2pp[field] for field in f]
        dtype = [(ff, np.float64) for ff in our_names]
        res["discrete"][name] = np.empty(res["n_samps"][name], dtype=dtype)
    e = edf_get_float_data(edf).contents.fe
    vals = _to_list(e, res["edf_fields"][name], res["eye_idx"])
    off = res["offsets"][name]
    for ff, vv in zip(res["discrete"][name].dtype.names, vals):
        res["discrete"][name][ff][off] = vv
    res["offsets"][name] += 1

def _handle_pass(edf, res):
    """Events we don't care about or haven't had to care about yet."""
    pass


def _handle_fixation_update(edf, res):
    """FIXUPDATE."""
    raise NotImplementedError


def _handle_version(res):
    """EDFAPI VERSION."""
    version = edf_get_version()
    res["info"]["edfapi_version"] = version.decode("utf-8")


# element_handlers maps the various EDF file element types to the
# element handler function that should be called.

_element_handlers = dict(
    RECORDING_INFO=_handle_recording_info,
    SAMPLE_TYPE=_handle_sample,
    MESSAGEEVENT=_handle_message,
    ENDFIX=partial(_handle_end, name="fixations"),
    ENDSACC=partial(_handle_end, name="saccades"),
    ENDBLINK=partial(_handle_end, name="blinks"),
    BUTTONEVENT=partial(_handle_end, name="buttons"),
    INPUTEVENT=partial(_handle_end, name="inputs"),
    STARTFIX=_handle_pass,
    STARTSACC=_handle_pass,
    STARTBLINK=_handle_pass,
    STARTPARSE=_handle_pass,
    FIXUPDATE=_handle_pass,
    ENDPARSE=_handle_pass,
    NO_PENDING_ITEMS=_handle_pass,  # context manager
    BREAKPARSE=_handle_pass,
    STARTSAMPLES=_handle_pass,
    ENDSAMPLES=_handle_pass,
    STARTEVENTS=_handle_pass,
    ENDEVENTS=_handle_pass,
    VERSION=_handle_version,
)
