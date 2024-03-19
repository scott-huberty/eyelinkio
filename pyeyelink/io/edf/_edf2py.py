# -*- coding: utf-8 -*-
"""Wrapper for libedfapi.so"""

import struct
import sys
from ctypes import (c_int, Structure, c_char, c_char_p, c_ubyte,
                    c_short, c_ushort, c_uint, c_float, POINTER, CDLL, util)

# find and load the library
if sys.platform.startswith('win') and (8 * struct.calcsize("P") == 64):
    name = 'edfapi64'  # on windows you can install both
else:
    name = 'edfapi'
fname = util.find_library(name)
if fname is None:
    raise OSError('edfapi not found')
edfapi = CDLL(fname)


# Extract the functions we need
class LSTRING(Structure):
    pass


LSTRING.__slots__ = ['len', 'c']
LSTRING._fields_ = [('len', c_short), ('c', c_char)]


class FSAMPLE(Structure):
    pass


cf = c_float
cf2 = c_float * 2
FSAMPLE.__slots__ = [
    'time', 'px', 'py', 'hx', 'hy', 'pa', 'gx', 'gy', 'rx', 'ry',
    'gxvel', 'gyvel', 'hxvel', 'hyvel', 'rxvel', 'ryvel', 'fgxvel', 'fgyvel',
    'fhxvel', 'fhyvel', 'frxvel', 'fryvel', 'hdata', 'flags', 'input',
    'buttons', 'htype', 'errors']
FSAMPLE._fields_ = [
    ('time', c_uint), ('px', cf2), ('py', cf2), ('hx', cf2),
    ('hy', cf2), ('pa', cf2), ('gx', cf2), ('gy', cf2),
    ('rx', cf), ('ry', cf), ('gxvel', cf2), ('gyvel', cf2),
    ('hxvel', cf2), ('hyvel', cf2), ('rxvel', cf2), ('ryvel', cf2),
    ('fgxvel', cf2), ('fgyvel', cf2), ('fhxvel', cf2), ('fhyvel', cf2),
    ('frxvel', cf2), ('fryvel', cf2), ('hdata', c_short * 8),
    ('flags', c_ushort), ('input', c_ushort), ('buttons', c_ushort),
    ('htype', c_short), ('errors', c_ushort)]


class FEVENT(Structure):
    pass


FEVENT.__slots__ = [
    'time', 'type', 'read', 'sttime', 'entime', 'hstx', 'hsty', 'gstx', 'gsty',
    'sta', 'henx', 'heny', 'genx', 'geny', 'ena', 'havx', 'havy',
    'gavx', 'gavy', 'ava', 'avel', 'pvel', 'svel', 'evel', 'supd_x',
    'eupd_x', 'supd_y', 'eupd_y', 'eye', 'status', 'flags', 'input', 'buttons',
    'parsedby', 'message']
FEVENT._fields_ = [
    ('time', c_uint), ('type', c_short), ('read', c_ushort),
    ('sttime', c_uint), ('entime', c_uint), ('hstx', cf), ('hsty', cf),
    ('gstx', cf), ('gsty', cf), ('sta', cf), ('henx', cf), ('heny', cf),
    ('genx', cf), ('geny', cf), ('ena', cf), ('havx', cf), ('havy', cf),
    ('gavx', cf), ('gavy', cf), ('ava', cf), ('avel', cf), ('pvel', cf),
    ('svel', cf), ('evel', cf), ('supd_x', cf), ('eupd_x', cf),
    ('supd_y', cf), ('eupd_y', cf), ('eye', c_short), ('status', c_ushort),
    ('flags', c_ushort), ('input', c_ushort), ('buttons', c_ushort),
    ('parsedby', c_ushort), ('message', POINTER(LSTRING))]


class RECORDINGS(Structure):
    pass


RECORDINGS.__slots__ = [
    'time', 'sample_rate', 'eflags', 'sflags', 'state', 'record_type',
    'pupil_type', 'recording_mode', 'filter_type', 'pos_type', 'eye']
RECORDINGS._fields_ = [
    ('time', c_uint), ('sample_rate', cf), ('eflags', c_ushort),
    ('sflags', c_ushort), ('state', c_ubyte), ('record_type', c_ubyte),
    ('pupil_type', c_ubyte), ('recording_mode', c_ubyte),
    ('filter_type', c_ubyte), ('pos_type', c_ubyte), ('eye', c_ubyte)]


class EDFFILE(Structure):
    pass


edf_open_file = edfapi.edf_open_file
edf_open_file.argtypes = [c_char_p, c_int, c_int, c_int, POINTER(c_int)]
edf_open_file.restype = POINTER(EDFFILE)

edf_close_file = edfapi.edf_close_file
edf_close_file.argtypes = [POINTER(EDFFILE)]
edf_close_file.restype = c_int

edf_get_next_data = edfapi.edf_get_next_data
edf_get_next_data.argtypes = [POINTER(EDFFILE)]
edf_get_next_data.restype = c_int

edf_get_preamble_text_length = edfapi.edf_get_preamble_text_length
edf_get_preamble_text_length.argtypes = [POINTER(EDFFILE)]
edf_get_preamble_text_length.restype = c_int

edf_get_preamble_text = edfapi.edf_get_preamble_text
edf_get_preamble_text.argtypes = [POINTER(EDFFILE), c_char_p, c_int]
edf_get_preamble_text.restype = c_int

edf_get_recording_data = edfapi.edf_get_recording_data
edf_get_recording_data.argtypes = [POINTER(EDFFILE)]
edf_get_recording_data.restype = POINTER(RECORDINGS)

edf_get_sample_data = edfapi.edf_get_sample_data
edf_get_sample_data.argtypes = [POINTER(EDFFILE)]
edf_get_sample_data.restype = POINTER(FSAMPLE)

edf_get_event_data = edfapi.edf_get_event_data
edf_get_event_data.argtypes = [POINTER(EDFFILE)]
edf_get_event_data.restype = POINTER(FEVENT)

"""
from ctypes import Union

class IMESSAGE(Structure):
    pass

IMESSAGE.__slots__ = ['time', 'type', 'length', 'text']
IMESSAGE._fields_ = [('time', c_uint), ('type', c_short), ('length', c_ushort),
                     ('text', c_ubyte * 260)]


class IOEVENT(Structure):
    pass

IOEVENT.__slots__ = ['time', 'type', 'data']
IOEVENT._fields_ = [('time', c_uint), ('type', c_short), ('data', c_ushort)]


class ALLF_DATA(Union):
    pass

ALLF_DATA.__slots__ = ['fe', 'im', 'io', 'fs', 'rec']
ALLF_DATA._fields_ = [('fe', FEVENT), ('im', IMESSAGE), ('io', IOEVENT),
                      ('fs', FSAMPLE), ('rec', RECORDINGS)]

edf_get_float_data = edfapi.edf_get_float_data
edf_get_float_data.argtypes = [POINTER(EDFFILE)]
edf_get_float_data.restype = POINTER(ALLF_DATA)

edf_get_sample_close_to_time = edfapi.edf_get_sample_close_to_time
edf_get_sample_close_to_time.argtypes = [POINTER(EDFFILE), c_uint]
edf_get_sample_close_to_time.restype = POINTER(ALLF_DATA)

edf_get_element_count = edfapi.edf_get_element_count
edf_get_element_count.argtypes = [POINTER(EDFFILE)]
edf_get_element_count.restype = c_uint

edf_get_revision = edfapi.edf_get_revision
edf_get_revision.argtypes = [POINTER(EDFFILE)]
edf_get_revision.restype = c_int

edf_get_eyelink_revision = edfapi.edf_get_eyelink_revision
edf_get_eyelink_revision.argtypes = [POINTER(EDFFILE)]
edf_get_eyelink_revision.restype = c_int

edf_set_trial_identifier = edfapi.edf_set_trial_identifier
edf_set_trial_identifier.argtypes = [POINTER(EDFFILE), String, String]
edf_set_trial_identifier.restype = c_int

edf_get_start_trial_identifier = edfapi.edf_get_start_trial_identifier
edf_get_start_trial_identifier.argtypes = [POINTER(EDFFILE)]
if sizeof(c_int) == sizeof(c_void_p):
    edf_get_start_trial_identifier.restype = ReturnString
else:
    edf_get_start_trial_identifier.restype = String
    edf_get_start_trial_identifier.errcheck = ReturnString

edf_get_end_trial_identifier = edfapi.edf_get_end_trial_identifier
edf_get_end_trial_identifier.argtypes = [POINTER(EDFFILE)]
if sizeof(c_int) == sizeof(c_void_p):
    edf_get_end_trial_identifier.restype = ReturnString
else:
    edf_get_end_trial_identifier.restype = String
    edf_get_end_trial_identifier.errcheck = ReturnString

edf_get_trial_count = edfapi.edf_get_trial_count
edf_get_trial_count.argtypes = [POINTER(EDFFILE)]
edf_get_trial_count.restype = c_int

edf_jump_to_trial = edfapi.edf_jump_to_trial
edf_jump_to_trial.argtypes = [POINTER(EDFFILE), c_int]
edf_jump_to_trial.restype = c_int


class TRIAL(Structure):
    pass

TRIAL.__slots__ = ['rec', 'duration', 'starttime', 'endtime']
TRIAL._fields_ = [('rec', POINTER(RECORDINGS)), ('duration', c_uint),
                  ('starttime', c_uint), ('endtime', c_uint)]


edf_get_trial_header = edfapi.edf_get_trial_header
edf_get_trial_header.argtypes = [POINTER(EDFFILE), POINTER(TRIAL)]
edf_get_trial_header.restype = c_int

edf_goto_previous_trial = edfapi.edf_goto_previous_trial
edf_goto_previous_trial.argtypes = [POINTER(EDFFILE)]
edf_goto_previous_trial.restype = c_int

edf_goto_next_trial = edfapi.edf_goto_next_trial
edf_goto_next_trial.argtypes = [POINTER(EDFFILE)]
edf_goto_next_trial.restype = c_int

edf_goto_trial_with_start_time = edfapi.edf_goto_trial_with_start_time
edf_goto_trial_with_start_time.argtypes = [POINTER(EDFFILE), c_uint]
edf_goto_trial_with_start_time.restype = c_int

edf_goto_trial_with_end_time = edfapi.edf_goto_trial_with_end_time
edf_goto_trial_with_end_time.argtypes = [POINTER(EDFFILE), c_uint]
edf_goto_trial_with_end_time.restype = c_int

edf_set_bookmark = edfapi.edf_set_bookmark
edf_set_bookmark.argtypes = [POINTER(EDFFILE), POINTER(BOOKMARK)]
edf_set_bookmark.restype = c_int

edf_free_bookmark = edfapi.edf_free_bookmark
edf_free_bookmark.argtypes = [POINTER(EDFFILE), POINTER(BOOKMARK)]
edf_free_bookmark.restype = c_int

edf_goto_bookmark = edfapi.edf_goto_bookmark
edf_goto_bookmark.argtypes = [POINTER(EDFFILE), POINTER(BOOKMARK)]
edf_goto_bookmark.restype = c_int

goto_next_bookmark = edfapi.edf_goto_next_bookmark
goto_next_bookmark.argtypes = [POINTER(EDFFILE)]
goto_next_bookmark.restype = c_int

edf_goto_previous_bookmark = edfapi.edf_goto_previous_bookmark
edf_goto_previous_bookmark.argtypes = [POINTER(EDFFILE)]
edf_goto_previous_bookmark.restype = c_int

edf_get_version = edfapi.edf_get_version
edf_get_version.argtypes = []
if sizeof(c_int) == sizeof(c_void_p):
    edf_get_version.restype = ReturnString
else:
    edf_get_version.restype = String
    edf_get_version.errcheck = ReturnString

edf_get_event = edfapi.edf_get_event
edf_get_event.argtypes = [POINTER(ALLF_DATA)]
edf_get_event.restype = POINTER(FEVENT)

edf_get_sample = edfapi.edf_get_sample
edf_get_sample.argtypes = [POINTER(ALLF_DATA)]
edf_get_sample.restype = POINTER(FSAMPLE)

edf_get_recording = edfapi.edf_get_recording
edf_get_recording.argtypes = [POINTER(ALLF_DATA)]
edf_get_recording.restype = POINTER(RECORDINGS)

edf_get_uncorrected_raw_pupil = edfapi.edf_get_uncorrected_raw_pupil
edf_get_uncorrected_raw_pupil.argtypes = [POINTER(EDFFILE), POINTER(FSAMPLE),
                                          c_int, POINTER(c_float)]
edf_get_uncorrected_raw_pupil.restype = None

edf_get_uncorrected_raw_cr = edfapi.edf_get_uncorrected_raw_cr
edf_get_uncorrected_raw_cr.argtypes = [POINTER(EDFFILE), POINTER(FSAMPLE),
                                       c_int, POINTER(c_float)]
edf_get_uncorrected_raw_cr.restype = None

edf_get_uncorrected_pupil_area = edfapi.edf_get_uncorrected_pupil_area
edf_get_uncorrected_pupil_area.argtypes = [POINTER(EDFFILE), POINTER(FSAMPLE),
                                           c_int]
edf_get_uncorrected_pupil_area.restype = c_uint

edf_get_uncorrected_cr_area = edfapi.edf_get_uncorrected_cr_area
edf_get_uncorrected_cr_area.argtypes = [POINTER(EDFFILE), POINTER(FSAMPLE),
                                        c_int]
edf_get_uncorrected_cr_area.restype = c_uint

edf_get_pupil_dimension = edfapi.edf_get_pupil_dimension
edf_get_pupil_dimension.argtypes = [POINTER(EDFFILE), POINTER(FSAMPLE), c_int,
                                    POINTER(c_uint)]
edf_get_pupil_dimension.restype = None

edf_get_cr_dimension = edfapi.edf_get_cr_dimension
edf_get_cr_dimension.argtypes = [POINTER(EDFFILE), POINTER(FSAMPLE),
                                 POINTER(c_uint)]
edf_get_cr_dimension.restype = None

edf_get_window_position = edfapi.edf_get_window_position
edf_get_window_position.argtypes = [POINTER(EDFFILE), POINTER(FSAMPLE),
                                    POINTER(c_uint)]
edf_get_window_position.restype = None

edf_get_pupil_cr = edfapi.edf_get_pupil_cr
edf_get_pupil_cr.argtypes = [POINTER(EDFFILE), POINTER(FSAMPLE), c_int,
                             POINTER(c_float)]
edf_get_pupil_cr.restype = None

edf_get_uncorrected_cr2_area = edfapi.edf_get_uncorrected_cr2_area
edf_get_uncorrected_cr2_area.argtypes = [POINTER(EDFFILE), POINTER(FSAMPLE),
                                         c_int]
edf_get_uncorrected_cr2_area.restype = c_uint

edf_get_uncorrected_raw_cr2 = edfapi.edf_get_uncorrected_raw_cr2
edf_get_uncorrected_raw_cr2.argtypes = [POINTER(EDFFILE), POINTER(FSAMPLE),
                                        c_int, POINTER(c_float)]
edf_get_uncorrected_raw_cr2.restype = None

edf_set_log_function = edfapi.edf_set_log_function
edf_set_log_function.argtypes = [CFUNCTYPE(UNCHECKED(None), String)]
edf_set_log_function.restype = None
"""
