
# uC chip interface for async/neuromorphic test chips

This firmware project is built to have a reusable interface for testing async/neuromorphic chips, also known as Device under Test (DuT).

The goal is that the firmware is free of any application-specific integrated circuit (ASIC) or printed circuit board (PCB) specific code. The User provides this configuration at runtime via an easy-to-use mid-level API. We are keeping the firmware maintainable and portable.

### Key features are:
 - different Async, SPI, I2C interfaces and I/O pin functionality
 - every action and incoming data is timestamped and reported 
 - all actions can be precisely timed with ~100us precision
 - simple mid-level python API
 - defensively programmed with many error notifications

### Currently supported uC (MicroController):
 - Teensy 4.1 (recommended for device testing)
 - Teensy 4.0
 - Arduino Zero (recommended for firmware development - debugger)
 - Arduino MKR variants

### Project home
The project is located at https://github.com/olerichter/uC-chip-interface

The documentation can be found at https://olerichter.github.io/uC-chip-interface

# For fruther description see [documentation main page](docs/main.md)

## [Changelog](CHANGELOG.md)