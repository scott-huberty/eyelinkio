"""Convert EyeLink EDF files to ASCII (.asc) format."""

import ctypes as ct
import math
from datetime import datetime
from pathlib import Path

from . import _defines as defines
from ._defines import event_constants
from .read import _edf_open, has_edfapi, why_not

try:
    from ._edf2py import (
        edf_get_float_data,
        edf_get_next_data,
        edf_get_preamble_text,
        edf_get_preamble_text_length,
        edf_get_version,
    )
except OSError:
    pass

_MISSING_THRESH = 1.0e8  # gaze values >= this are considered missing
_UINT32_MOD = 0x100000000  # 2^32 for unsigned duration wrap


def to_asc(edf_path, asc_path=None, *, include_input=True):
    """Convert an EyeLink EDF file to ASCII (.asc) format.

    Parameters
    ----------
    edf_path : path-like
        The path to the EDF file to convert.
    asc_path : path-like or None
        The output path for the ASCII file. If None, the EDF file
        extension is replaced with '.asc'.
    include_input : bool
        Whether to include INPUT port data in SAMPLES config and sample
        lines. Corresponds to the ``-input`` flag in edf2asc. Older
        versions of edf2asc (3.1) omit INPUT by default; newer versions
        (4.2+) include it.

    Returns
    -------
    asc_path : Path
        The path to the generated ASCII file.
    """
    if not has_edfapi:
        raise OSError(f"Could not load EDF api: {why_not}")
    edf_path = Path(edf_path)
    if not edf_path.is_file():
        raise OSError(f"File {edf_path} does not exist")
    if asc_path is None:
        asc_path = edf_path.with_suffix(".asc")
    asc_path = Path(asc_path)

    with _edf_open(edf_path) as edf, open(asc_path, "w") as out:
        writer = _AscWriter(edf_path, out, include_input=include_input)
        writer.write_preamble(edf)

        etype = None
        while etype != event_constants.get("NO_PENDING_ITEMS"):
            etype = edf_get_next_data(edf)
            if etype not in event_constants:
                raise RuntimeError(f"Unknown element type: {etype}")
            ets = event_constants[etype]
            handler = _asc_handlers.get(ets, _noop)
            handler(writer, edf)

    return asc_path


class _AscWriter:
    """Encapsulates state for streaming EDF-to-ASC conversion."""

    def __init__(self, edf_path, out, *, include_input=True):
        self.edf_path = edf_path
        self.out = out
        self.include_input = include_input
        self.in_recording = False
        self.eye_idx = None  # 0=left, 1=right, 2=binocular
        self.sample_rate = 0.0
        self.recording_mode = 0
        self.pupil_type = 0
        self.filter_type = 0
        self.sflags = 0
        self.last_rx = 0.0
        self.last_ry = 0.0
        self._rx_sum = 0.0
        self._ry_sum = 0.0
        self._rx_count = 0
        self._ry_count = 0
        self._res_by_time = {}  # {time: (rx, ry)} for ESACC lookups

    def write_preamble(self, edf):
        """Write the file preamble (header lines)."""
        # Get raw preamble from EDF
        tlen = edf_get_preamble_text_length(edf)
        txt = ct.create_string_buffer(tlen)
        edf_get_preamble_text(edf, txt, tlen + 1)
        preamble = txt.value.decode("ASCII").rstrip("\n")

        # edf_get_version() returns the full version string including
        # platform and build date, e.g.:
        # "4.2.1197.0 Linux   standalone Sep 27 2024"
        version = edf_get_version()
        if isinstance(version, bytes):
            version = version.decode("utf-8")

        timestamp = datetime.now().strftime("%c")

        # Write CONVERTED FROM line (matches edf2asc format)
        self.out.write(
            f"** CONVERTED FROM {self.edf_path} "
            f"using edfapi {version} on {timestamp}\n"
        )
        # Write the raw preamble (already has ** prefixes)
        self.out.write(preamble + "\n")
        # Ensure preamble ends with a closing ** line
        if not preamble.rstrip().endswith("**"):
            self.out.write("**\n")
        # Blank line after preamble
        self.out.write("\n")

    def _eye_char(self, eye_val):
        """Convert eye index to character."""
        if eye_val == 0:
            return "L"
        elif eye_val == 1:
            return "R"
        return "L"  # default

    def _build_events_config(self):
        """Build the EVENTS config line."""
        parts = ["EVENTS"]
        if self.sflags & defines.SAMPLE_GAZEXY:
            parts.append("GAZE")
        elif self.sflags & defines.SAMPLE_HREFXY:
            parts.append("HREF")
        elif self.sflags & defines.SAMPLE_PUPILXY:
            parts.append("RAW")
        if self.eye_idx == 0:
            parts.append("LEFT")
        elif self.eye_idx == 1:
            parts.append("RIGHT")
        else:
            parts.extend(["LEFT", "RIGHT"])
        parts.append("RATE")
        parts.append(f"{self.sample_rate:>7.2f}")
        if self.recording_mode != 0:
            parts.append("TRACKING")
            parts.append("CR")
        parts.append("FILTER")
        parts.append(str(self.filter_type))
        return "\t".join(parts)

    def _build_samples_config(self):
        """Build the SAMPLES config line."""
        parts = ["SAMPLES"]
        if self.sflags & defines.SAMPLE_GAZEXY:
            parts.append("GAZE")
        elif self.sflags & defines.SAMPLE_HREFXY:
            parts.append("HREF")
        elif self.sflags & defines.SAMPLE_PUPILXY:
            parts.append("RAW")
        if self.eye_idx == 0:
            parts.append("LEFT")
        elif self.eye_idx == 1:
            parts.append("RIGHT")
        else:
            parts.extend(["LEFT", "RIGHT"])
        if self.sflags & defines.SAMPLE_HEADPOS:
            parts.append("HTARGET")
        parts.append("RATE")
        parts.append(f"{self.sample_rate:>7.2f}")
        if self.recording_mode != 0:
            parts.append("TRACKING")
            parts.append("CR")
        parts.append("FILTER")
        parts.append(str(self.filter_type))
        if self.include_input and self.sflags & defines.SAMPLE_INPUTS:
            parts.append("INPUT")
        return "\t".join(parts)


def _write_recording_info(writer, edf):
    """Handle RECORDING_INFO — emit START or END block."""
    rec = edf_get_float_data(edf).contents.rec
    if rec.state != 0:
        if writer.in_recording:
            return  # skip duplicate recording start
        # Recording started
        writer.eye_idx = rec.eye - 1  # edfapi uses 1-based
        writer.sample_rate = rec.sample_rate
        writer.pupil_type = rec.pupil_type
        writer.recording_mode = rec.recording_mode
        writer.filter_type = rec.filter_type
        writer.sflags = rec.sflags
        writer.in_recording = True
        writer.last_rx = 0.0
        writer.last_ry = 0.0
        writer._rx_sum = 0.0
        writer._ry_sum = 0.0
        writer._rx_count = 0
        writer._ry_count = 0
        writer._res_by_time = {}

        # Eye name for START line
        if writer.eye_idx == 0:
            eye_name = "LEFT"
        elif writer.eye_idx == 1:
            eye_name = "RIGHT"
        else:
            eye_name = "LEFT\tRIGHT"

        # Pupil type
        pupil_name = "AREA" if writer.pupil_type == 0 else "DIAMETER"

        out = writer.out
        out.write(f"START\t{rec.time} \t{eye_name}\tSAMPLES\tEVENTS\n")
        out.write("PRESCALER\t1\n")
        out.write("VPRESCALER\t1\n")
        out.write(f"PUPIL\t{pupil_name}\n")
        out.write(writer._build_events_config() + "\n")
        out.write(writer._build_samples_config() + "\n")
    else:
        # Recording stopped — END RES uses average resolution
        writer.in_recording = False
        rx = writer._rx_sum / writer._rx_count if writer._rx_count else 0.0
        ry = writer._ry_sum / writer._ry_count if writer._ry_count else 0.0
        writer.out.write(
            f"END\t{rec.time} \tSAMPLES\tEVENTS\tRES"
            f"\t{rx:7.2f}\t{ry:7.2f}\n"
        )


def _write_sample(writer, edf):
    """Handle SAMPLE_TYPE — emit a sample data line."""
    fs = edf_get_float_data(edf).contents.fs
    out = writer.out
    # For binocular, start with left eye
    idx = writer.eye_idx if writer.eye_idx < 2 else 0

    # Track resolution for END line (average) and ESACC (start/end average)
    if fs.rx > 0:
        writer.last_rx = fs.rx
        writer._rx_sum += fs.rx
        writer._rx_count += 1
    if fs.ry > 0:
        writer.last_ry = fs.ry
        writer._ry_sum += fs.ry
        writer._ry_count += 1
    if fs.rx > 0 or fs.ry > 0:
        rx = fs.rx if fs.rx > 0 else 0.0
        ry = fs.ry if fs.ry > 0 else 0.0
        writer._res_by_time[fs.time] = (rx, ry)

    # Timestamp
    out.write(f"{fs.time}")

    if writer.eye_idx < 2:
        # Monocular
        _write_eye_sample(out, fs, idx)
    else:
        # Binocular: left then right
        _write_eye_sample(out, fs, 0)
        _write_eye_sample(out, fs, 1)

    # Input field (if enabled and available in sflags)
    if writer.include_input and writer.sflags & defines.SAMPLE_INPUTS:
        out.write(f"\t{float(fs.input):7.1f}")

    # HTARGET data and status marker
    if writer.sflags & defines.SAMPLE_HEADPOS:
        hd0_raw = fs.hdata[0]
        if hd0_raw == -32768:  # Missing HTARGET data
            out.write("\t... \t   .\t   .\t   . M............\n")
        else:
            hd0 = float(hd0_raw)
            hd1 = float(fs.hdata[1])
            hd2 = float(fs.hdata[2]) / 10.0
            out.write(
                f"\t... \t{hd0:7.1f}\t{hd1:7.1f}"
                f"\t{hd2:7.1f} .............\n"
            )
    else:
        out.write(" .............\n")


def _write_eye_sample(out, fs, eye_idx):
    """Write gaze x, y, pupil for one eye."""
    gx = fs.gx[eye_idx]
    gy = fs.gy[eye_idx]
    pa = fs.pa[eye_idx]

    if gx >= _MISSING_THRESH or gy >= _MISSING_THRESH:
        out.write("\t   .\t   .")
    else:
        out.write(f"\t{gx:7.1f}\t{gy:7.1f}")
    out.write(f"\t{pa:7.1f}")


def _write_message(writer, edf):
    """Handle MESSAGEEVENT — emit MSG line."""
    fe = edf_get_float_data(edf).contents.fe
    nbytes = fe.message.contents.len + 1
    msg = ct.string_at(ct.byref(fe.message[0]), nbytes)[2:]
    msg = msg.decode("UTF-8", errors="replace")
    msg = "".join([i if ord(i) < 128 else "" for i in msg])
    msg = msg.rstrip("\r\n")
    writer.out.write(f"MSG\t{fe.sttime} {msg}\n")


def _write_button(writer, edf):
    """Handle BUTTONEVENT — emit BUTTON line(s)."""
    fe = edf_get_float_data(edf).contents.fe
    time = fe.sttime
    button_data = fe.buttons
    # High byte: changed mask, low byte: current state
    changed = (button_data >> 8) & 0xFF
    state = button_data & 0xFF
    for bit in range(8):
        if changed & (1 << bit):
            button_id = bit + 1
            pressed = 1 if (state & (1 << bit)) else 0
            writer.out.write(f"BUTTON\t{time}\t{button_id}\t{pressed}\n")


def _write_input(writer, edf):
    """Handle INPUTEVENT — emit INPUT line."""
    fe = edf_get_float_data(edf).contents.fe
    writer.out.write(f"INPUT\t{fe.sttime}\t{fe.input}\n")


def _write_start_fix(writer, edf):
    """Handle STARTFIX — emit SFIX line."""
    fe = edf_get_float_data(edf).contents.fe
    eye = writer._eye_char(fe.eye)
    prefix = f"SFIX {eye}".ljust(9)
    writer.out.write(f"{prefix}{fe.sttime}\n")


def _write_end_fix(writer, edf):
    """Handle ENDFIX — emit EFIX line."""
    fe = edf_get_float_data(edf).contents.fe
    eye = writer._eye_char(fe.eye)
    prefix = f"EFIX {eye}".ljust(9)
    speriod = round(1000.0 / writer.sample_rate)
    dur = (fe.entime - fe.sttime) % _UINT32_MOD + speriod
    writer.out.write(
        f"{prefix}{fe.sttime}\t{fe.entime}\t{dur}"
        f"\t{fe.gavx:7.1f}\t{fe.gavy:7.1f}\t{round(fe.ava):7d}\n"
    )


def _write_start_sacc(writer, edf):
    """Handle STARTSACC — emit SSACC line."""
    fe = edf_get_float_data(edf).contents.fe
    eye = writer._eye_char(fe.eye)
    prefix = f"SSACC {eye}".ljust(9)
    writer.out.write(f"{prefix}{fe.sttime}\n")


def _write_end_sacc(writer, edf):
    """Handle ENDSACC — emit ESACC line."""
    fe = edf_get_float_data(edf).contents.fe
    eye = writer._eye_char(fe.eye)
    prefix = f"ESACC {eye}".ljust(9)
    speriod = round(1000.0 / writer.sample_rate)
    dur = (fe.entime - fe.sttime) % _UINT32_MOD + speriod

    # Format gaze coordinates (missing values → "   .")
    gstx_miss = fe.gstx >= _MISSING_THRESH or fe.gsty >= _MISSING_THRESH
    genx_miss = fe.genx >= _MISSING_THRESH or fe.geny >= _MISSING_THRESH
    if gstx_miss:
        sx_str = "\t   .\t   ."
    else:
        sx_str = f"\t{fe.gstx:7.1f}\t{fe.gsty:7.1f}"
    if genx_miss:
        ex_str = "\t   .\t   ."
    else:
        ex_str = f"\t{fe.genx:7.1f}\t{fe.geny:7.1f}"

    # Compute saccade amplitude in degrees using average of resolution
    # at saccade start and end (pixel-per-degree varies across screen)
    dx_px = fe.genx - fe.gstx
    dy_px = fe.geny - fe.gsty
    st_res = writer._res_by_time.get(fe.sttime)
    en_res = writer._res_by_time.get(fe.entime)
    if st_res and en_res and st_res[0] > 0 and en_res[0] > 0:
        res_x = (st_res[0] + en_res[0]) / 2.0
        res_y = (st_res[1] + en_res[1]) / 2.0
    else:
        res_x = fe.supd_x if fe.supd_x > 0 else writer.last_rx
        res_y = fe.supd_y if fe.supd_y > 0 else writer.last_ry
    if res_x > 0 and res_y > 0:
        dx_deg = dx_px / res_x
        dy_deg = dy_px / res_y
        amplitude = math.sqrt(dx_deg * dx_deg + dy_deg * dy_deg)
    else:
        amplitude = 0.0

    # Large amplitudes (from missing gaze) use scientific notation
    if amplitude >= 1e5:
        amp_str = f"{amplitude:8.1e}"
    else:
        amp_str = f"{amplitude:7.2f}"

    writer.out.write(
        f"{prefix}{fe.sttime}\t{fe.entime}\t{dur}"
        f"{sx_str}{ex_str}"
        f"\t{amp_str}\t{round(fe.pvel):7d}\n"
    )


def _write_start_blink(writer, edf):
    """Handle STARTBLINK — emit SBLINK line."""
    fe = edf_get_float_data(edf).contents.fe
    eye = writer._eye_char(fe.eye)
    prefix = f"SBLINK {eye}".ljust(9)
    writer.out.write(f"{prefix}{fe.sttime}\n")


def _write_end_blink(writer, edf):
    """Handle ENDBLINK — emit EBLINK line."""
    fe = edf_get_float_data(edf).contents.fe
    eye = writer._eye_char(fe.eye)
    prefix = f"EBLINK {eye}".ljust(9)
    speriod = round(1000.0 / writer.sample_rate)
    dur = (fe.entime - fe.sttime) % _UINT32_MOD + speriod
    writer.out.write(f"{prefix}{fe.sttime}\t{fe.entime}\t{dur}\n")


def _noop(writer, edf):
    """No-op handler for events that produce no ASC output."""
    pass


# Map EDF element type names to handler functions
_asc_handlers = {
    "RECORDING_INFO": _write_recording_info,
    "SAMPLE_TYPE": _write_sample,
    "MESSAGEEVENT": _write_message,
    "BUTTONEVENT": _write_button,
    "INPUTEVENT": _write_input,
    "STARTFIX": _write_start_fix,
    "ENDFIX": _write_end_fix,
    "STARTSACC": _write_start_sacc,
    "ENDSACC": _write_end_sacc,
    "STARTBLINK": _write_start_blink,
    "ENDBLINK": _write_end_blink,
    "STARTEVENTS": _noop,
    "ENDEVENTS": _noop,
    "STARTPARSE": _noop,
    "ENDPARSE": _noop,
    "FIXUPDATE": _noop,
    "BREAKPARSE": _noop,
    "STARTSAMPLES": _noop,
    "ENDSAMPLES": _noop,
    "NO_PENDING_ITEMS": _noop,
}
