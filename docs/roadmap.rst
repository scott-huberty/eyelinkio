Roadmap
=======

This page describes some of the limitations of the current implementation, and
items in need of discussion.

- **Support for Binocular data**:
    The current implementation does not support
    reading binocular data. Adding this support will not be trivial.
    From a brief look, it appears that our code assumes that each call of
    ``edf_get_next_data`` will contain sample data (xpos, ypos, pupil size etc.)
    from a unique time point. But each call to ``edf_get_next_data`` returns data for a
    single eye, so in the case of binocular data, every 2 calls will return data for the
    same time point, but for different eyes (left, and right).

- **Support for all sample fields**:
    The current implementation only supports
    reading ``xpos``, ``ypos``, and ``pupil size`` sample fields. We should add support for
    reading other sample fields, such as head position, velocity, etc. This shouldn't be
    too difficult, but we will want to add a way to specify which fields to read in the
    API.

- **EDF Message string representation**:
    The current implementation represents the
    messages as byte strings (i.e. ``b'stimulus_presentation'``). This was inherited from
    the original implementation in pyeparse. I'm not sure whether this was to stay
    compatible with python 2, or if memory was a concern. We could just represent them as
    regular Python strings, but I will wait to see if anyone provides feedback on this
    before changing it.

- **Use of Named Arrays**:
    The current implementation stores data in named Numpy
    arrays, so that for example you can do ``edf["discrete"]["messages"]["msg"]`` to get
    an array of the message strings. This was inherited from the original pyeparse
    implementation. Named arrays are nice but add some complexity (and most users
    probably aren't familiar with them?). I'm not sure if we should keep them, or just
    use dictionaries instead. I will wait to see if anyone provides feedback on this.