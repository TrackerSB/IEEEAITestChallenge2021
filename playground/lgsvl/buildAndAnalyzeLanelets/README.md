Install opendrive2lanets (I did it from source but it should work also with pip install). Version is 1.2.0

The main.py patches the library in one place and extends it in few other places, but other than that, it should work out of the box.

Note that unless you install it from source after patching it, the GUI apps will not work (because they will bot use the patch!)

Requirements are listed in the requirements-39.txt file.

Tested using Python 3.9.5 on Mac OS.


