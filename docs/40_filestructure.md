# Source file structure

## Arduino code (firmware)
the uC firmware files are located in `firmware`. The main file is the firmware.ino, all files starting with `core_` handle the packet buffers and timed execution. The interfaces begin with `interface_`. The User can find all uC board-specific configurations in `uc_boards.h`, and all packet definitions and data structure for the PC communication are in `datatypes.h`.

## Python code (uC_api)
The Python code is in the module `uC_api` and can be imported with `import uC_api` when adding the repository root to the Python search path 
```python
import sys
sys.path.append('<path to git repo>')
import uC_api
```
For a more detailed description, look at the section API levels.

## Tests & Examples (tests)
tests can be found in `tests`. These scripts are good starting points for using the individual features. 
