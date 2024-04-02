The edf2pygen folder contains the files needed to use ctypesgen to create a
Python wrapper of the C EDF Access API. This directory is not needed as part
of a end user build / distribution.

Dependancies:
~~~~~~~~~~~~~

1. ctypesgen module: in your site-packages folder. Imay need to send the copy I
   have; forget if I have hacked at it or not.

2. edfapi.dll and edf.h: These are needed when ctypesgen is run to create 
   the wrapper. On non Windows OS, edfapi should be replaced with the same
   library version compiled for the platform in question. Header file should
   not need to be changed (the couple platform dependent defines have been
   stripped out as they are not of any use unless using an EyeLink2 with 
   Scene Camera.)

How to Create edf2py.py Wrapper
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Note dependancies mentioned above.

2. Open a cmd window and cd to this directory.

3. For Windows, if using MVS 2010:
    a. Run 'vsvars32.bat' to setup cmd env. for 32 bit build.

*Note: For Linux / OSX gcc is fine but details TBD.

4. Run the following to generate the edf2py.py file:

python ctypesgen.py --insert-file edf2py_extra.py --cpp="cl -EP" -a -l edfapi -o edf2py.py edf.h

5. Remove the edf_ prefix from all the python functions generated. This is
   just a matter of taste. ;)

6. Copy the following files to the edf2py source folder for distribution:
    a. edf2py.py
    b. edfapi.dll (or platform dependent equivelent lib)

=========================================

HOWTO: Make wrapper on Linux

1. Install ctypesgen.

2. Install EyeLink software.

3. Run "ctypesgen.py -a -l edfapi -o _edf2py.py /usr/include/edf.h"

The current version based on ideas from that file, but much simplified.
 
