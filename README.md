# Overview

## A PC interface for small and simple async and neuromorphic IC test chips

This firmware project is built to have a reusable interface for testing async/neuromorphic chips, also known as Device under Test (DuT).

The goal is that the firmware is free of any application-specific integrated circuit (ASIC) or printed circuit board (PCB) specific code. The User provides this configuration at runtime via an easy-to-use mid-level API. We are keeping the firmware maintainable and portable.

## Key features
 - different Async, SPI, I2C interfaces and I/O pin functionality
 - every action and incoming data is timestamped and reported, for transperency to limit search during testing scope
 - all actions can be precisely timed with ~100us precision
 - simple mid-level python API
 - defensively programmed with many error notifications, to track down errors during testing

## Currently supported uC (MicroController)
 - Teensy 4.1 (recommended for device testing)
 - Teensy 4.0
 - Arduino Zero (recommended for firmware development - debugger)
 - Arduino MKR variants

## Project home
The project is located at https://github.com/olerichter/uC-chip-interface-arduino

## Documentation
The documentation can be found at https://olerichter.github.io/uC-chip-interface-arduino
or in the folder `docs/`

To learn how to use and interface the uC read about the [API](docs/20_api_levels.md).

To learn more about the concept read about the [Architecture](docs/30_architecture.md).

## Known bugs and comming features

 - on SAMD21 uC (Zero, MKR), testing async interfaces via loopback is currently not working due to an unfixed bug in the interrupt priority.
   Regular DuT operation should work without problems.

for features that might be added on request and demand see [TODO](TODO.md)

## How to contribute

Contributions are very welcome. Please reach out and open a pull request!

Please base your pull request againced the branch dev as master only holds releases.

It would help us and your pull request if you add code/function docs and, ideally, if it makes sense to a test/example, 
please note down your changes in [CHANGELOG](CHANGELOG.md) below [Unreleased].

@people with direct repo access do not commit to main or dev directly. Do feature branches and pull requests! 

All DuT-specific files and higher-level APIs should be in their separate repositories.
