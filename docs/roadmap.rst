Roadmap
=======

This page describes some of the limitations of the current implementation, and
items in need of discussion.

- **Support for all sample fields**:
    The current implementation only supports
    reading ``xpos``, ``ypos``, and ``pupil size`` sample fields. We should add support for
    reading other sample fields, such as head position, velocity, etc. This shouldn't be
    too difficult, but we will want to add a way to specify which fields to read in the
    API.

- **Transfer this library to an organization**:
    I created this library under my personal GitHub account, but if it gains traction
    we can create an organization for it, so that other developers can have
    push access to the repository, access to the CI's etc.

- **EDF Message string representation**:
    The current implementation represents the
    messages as byte strings (i.e. ``b'stimulus_presentation'``). This was inherited from
    the original implementation in pyeparse. I'm not sure whether this was to stay
    compatible with python 2, or if memory was a concern. We could just represent them as
    regular Python strings, but I will wait to see if anyone provides feedback on this
    before changing it.

- **Use of structured Arrays**:
    The current implementation stores data in structured Numpy
    arrays, so that for example you can do ``edf["discrete"]["messages"]["msg"]`` to get
    an array of the message strings. This was inherited from the original pyeparse
    implementation. Structured arrays are nice but add some complexity (and most users
    probably aren't familiar with them?). I'm not sure if we should keep them, or just
    use dictionaries instead. I will wait to see if anyone provides feedback on this.

- **Support for other file formats**:
    If this library gains traction, we could add support for reading ASCII format files.
    To do this we should port the ``read_raw_eyelink code`` from MNE-Python, (and remove it
    from MNE-Python, such that MNE calls our function to read ASCII data).