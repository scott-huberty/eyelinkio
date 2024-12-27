"""
Defines for the EDF API.

This file contains all the define values from the edfapi header files.
A couple extra have been added as well.

Some of the constants are grouped into dicts, where both k,v and v,k entries
are added so it is easy to go from either the int -> str constant or str -> int
constant value for each.

The constants that are not grouped into sub dicts are available either as
variables within the defines module, or in dict form (named 'edf_constants')
where both k,v and v,k entries are added so it is easy to go from either the
int -> str constant or str -> int constant value for each.

Created on Sat Mar 15 09:40:17 2014

@author: Sol
"""


def create_constants(var_val_dict):
    # define function vars here.
    # They will be read and a constants dict with var_name:var_val
    # and var_val:var_name will be created abd returned

    constants = dict(
        [
            (key, val)
            for key, val in dict(var_val_dict).items()
            if (not key.startswith("_") and not callable(val))
        ]
    )
    constants.update([(val, key) for key, val in dict(constants).items()])
    return constants


# ************* EVENT TYPE CODES ***********
event_constants = create_constants(
    dict(
        SAMPLE_TYPE=200,
        # buffer = IEVENT, FEVENT, btype = IEVENT_BUFFER
        STARTPARSE=1,  # these only have time and eye data
        ENDPARSE=2,
        BREAKPARSE=10,
        # EYE DATA: contents determined by evt_data
        STARTBLINK=3,  # and by "read" data item
        ENDBLINK=4,  # all use IEVENT format
        STARTSACC=5,
        ENDSACC=6,
        STARTFIX=7,
        ENDFIX=8,
        FIXUPDATE=9,
        # buffer = (none, directly affects state), btype = CONTROL_BUFFER
        # control events: all put data into
        # the EDF_FILE or ILINKDATA status
        STARTSAMPLES=15,  # start of events in block
        ENDSAMPLES=16,  # end of samples in block
        STARTEVENTS=17,  # start of events in block
        ENDEVENTS=18,  # end of events in block
        # buffer = IMESSAGE, btype = IMESSAGE_BUFFER
        MESSAGEEVENT=24,  # user-definable text or data
        # buffer = IOEVENT, btype = IOEVENT_BUFFER
        BUTTONEVENT=25,  # button state change
        INPUTEVENT=28,  # change of input port
        LOST_DATA_EVENT=0x3F,  # NEW: Event flags gap in data stream
        NO_PENDING_ITEMS=0,
        RECORDING_INFO=30,
    )
)

# Missing data constants
MISSING_DATA = -32768  # data is missing (integer)
MISSING = -32768
INaN = -32768

eye_constants = create_constants(
    dict(
        # binocular data needs to ID the eye for events
        # samples need to index the data
        # These constants are used as eye identifiers
        LEFT_EYE=0,  # index and ID of eyes
        RIGHT_EYE=1,
        BINOCULAR=2,  # data for both eyes available
    )
)


pupil_constants = create_constants(dict(PUPIL_AREA=0, PUPIL_DIAMETER=1))

# ******** EYE SAMPLE DATA FORMATS ******
#
# The SAMPLE struct contains data from one 4-msec
# eye-tracker sample. The <flags> field has a bit for each
# type of data in the sample. Fields not read have 0 flag
# bits, and are set to MISSING_DATA
#
# flags to define what data is included in each sample.
# There is one bit for each type.  Total data for samples
# in a block is indicated by these bits in the <sam_data>
# field of ILINKDATA or EDF_FILE, and is updated by the
# STARTSAMPLES control event.

SAMPLE_LEFT = 0x8000  # data for these eye(s)
SAMPLE_RIGHT = 0x4000
SAMPLE_TIMESTAMP = 0x2000  # always for link, used to compress files
SAMPLE_PUPILXY = 0x1000  # pupil x,y pair
SAMPLE_HREFXY = 0x0800  # head-referenced x,y pair
SAMPLE_GAZEXY = 0x0400  # gaze x,y pair
SAMPLE_GAZERES = 0x0200  # gaze res (x,y pixels per degree) pair
SAMPLE_PUPILSIZE = 0x0100  # pupil size
SAMPLE_STATUS = 0x0080  # error flags
SAMPLE_INPUTS = 0x0040  # input data port
SAMPLE_BUTTONS = 0x0020  # button state: LSBy state, MSBy changes
SAMPLE_HEADPOS = 0x0010  # head-position: byte tells # words
SAMPLE_TAGGED = 0x0008  # reserved variable-length tagged
SAMPLE_UTAGGED = 0x0004  # user-defineabe variable-length tagged
SAMPLE_ADD_OFFSET = 0x0002  # if this flag is set for the sample add .5ms to
# the sample time

# ************ CONSTANTS FOR EVENTS ***********
# "read" flag contents in IEVENT
# time data
READ_ENDTIME = 0x0040  # end time (start time always read)

# non-position eye data:
READ_GRES = 0x0200  # gaze resolution xy
READ_SIZE = 0x0080  # pupil size
READ_VEL = 0x0100  # velocity (avg, peak)
READ_STATUS = 0x2000  # status (error word)
READ_BEG = 0x0001  # event has start data for vel,size,gres
READ_END = 0x0002  # event has end data for vel,size,gres
READ_AVG = 0x0004  # event has avg pupil size, velocity

# position eye data
READ_PUPILXY = 0x0400  # pupilxy REPLACES gaze, href data if read
READ_HREFXY = 0x0800
READ_GAZEXY = 0x1000
READ_BEGPOS = 0x0008  # position data for these parts of event
READ_ENDPOS = 0x0010
READ_AVGPOS = 0x0020

# RAW FILE/LINK CODES: REVERSE IN R/W
FRIGHTEYE_EVENTS = 0x8000  # has right eye events
FLEFTEYE_EVENTS = 0x4000  # has left eye events

# "event_types" flag in ILINKDATA or EDF_FILE
# tells what types of events were written by tracker
LEFTEYE_EVENTS = 0x8000  # has left eye events
RIGHTEYE_EVENTS = 0x4000  # has right eye events
BLINK_EVENTS = 0x2000  # has blink events
FIXATION_EVENTS = 0x1000  # has fixation events
FIXUPDATE_EVENTS = 0x0800  # has fixation updates
SACCADE_EVENTS = 0x0400  # has saccade events
MESSAGE_EVENTS = 0x0200  # has message events
BUTTON_EVENTS = 0x0040  # has button events
INPUT_EVENTS = 0x0020  # has input port events

# "event_data" flags in ILINKDATA or EDF_FILE
# tells what types of data were included in events by tracker
EVENT_VELOCITY = 0x8000  # has velocity data
EVENT_PUPILSIZE = 0x4000  # has pupil size data
EVENT_GAZERES = 0x2000  # has gaze resolution
EVENT_STATUS = 0x1000  # has status flags
EVENT_GAZEXY = 0x0400  # has gaze xy position
EVENT_HREFXY = 0x0200  # has head-ref xy position
EVENT_PUPILXY = 0x0100  # has pupil xy position
FIX_AVG_ONLY = 0x0008  # only avg. data to fixation evts
START_TIME_ONLY = 0x0004  # only start-time in start events
PARSEDBY_GAZE = 0x00C0  # how events were generated
PARSEDBY_HREF = 0x0080
PARSEDBY_PUPIL = 0x0040

# *********** STATUS FLAGS (samples and events) ***************
LED_TOP_WARNING = 0x0080  # marker is in border of image
LED_BOT_WARNING = 0x0040
LED_LEFT_WARNING = 0x0020
LED_RIGHT_WARNING = 0x0010
HEAD_POSITION_WARNING = 0x00F0  # head too far from calibr???
LED_EXTRA_WARNING = 0x0008  # glitch or extra markers
LED_MISSING_WARNING = 0x0004  # <2 good data points in last 100 msec)
HEAD_VELOCITY_WARNING = 0x0001  # head moving too fast
CALIBRATION_AREA_WARNING = 0x0002  # pupil out of good mapping area
MATH_ERROR_WARNING = 0x2000  # math error in proc. sample

# THESE CODES ONLY VALID FOR EYELINK II

# this sample interpolated to preserve sample rate
# usually because speed dropped due to missing pupil
# INTERP_SAMPLE_WARNING 0x1000

# pupil interpolated this sample
# usually means pupil loss or
# 500 Hz sample with CR but no pupil
#
INTERP_PUPIL_WARNING = 0x8000

# all CR-related errors
CR_WARNING = 0x0F00
CR_LEFT_WARNING = 0x0500
CR_RIGHT_WARNING = 0x0A00

# CR is actually lost
CR_LOST_WARNING = 0x0300
CR_LOST_LEFT_WARNING = 0x0100
CR_LOST_RIGHT_WARNING = 0x0200

# this sample has interpolated/held CR
CR_RECOV_WARNING = 0x0C00
CR_RECOV_LEFT_WARNING = 0x0400
CR_RECOV_RIGHT_WARNING = 0x0800

TFLAG_MISSING = 0x4000  # missing
TFLAG_ANGLE = 0x2000  # extreme target angle
TFLAG_NEAREYE = 0x1000  # target near eye so windows overlapping
# DISTANCE WARNINGS (limits set by remote_distance_warn_range command)
TFLAG_CLOSE = 0x0800  # distance vs. limits
TFLAG_FAR = 0x0400
# TARGET TO CAMERA EDGE  (margin set by remote_edge_warn_pixels command)
TFLAG_T_TSIDE = 0x0080  # target near edge of image (left, right, top, bottom)
TFLAG_T_BSIDE = 0x0040
TFLAG_T_LSIDE = 0x0020
TFLAG_T_RSIDE = 0x0010
# EYE TO CAMERA EDGE  (margin set by remote_edge_warn_pixels command)
TFLAG_E_TSIDE = 0x0008  # eye near edge of image (left, right, top, bottom)
TFLAG_E_BSIDE = 0x0004
TFLAG_E_LSIDE = 0x0002
TFLAG_E_RSIDE = 0x0001

PUPIL_ONLY_250 = 0
PUPIL_ONLY_500 = 1
PUPIL_CR = 2

EYELINK = 1
EYELINK_II = 2
EYELINK_1000 = 3

edf_constants = dict(
    [
        (k, v)
        for k, v in dict(locals()).items()
        if (not k.startswith("_") and not isinstance(v, dict))
    ]
)
