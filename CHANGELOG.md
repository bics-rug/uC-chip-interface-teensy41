# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added 
 - all executions are acklogage with timestamp to the PC
 - added support for Teensy 4.0 (MIMXR)
 - added support for Arduino MRKZero (SAMD21)
 - added software reset 
 - added python api level 1 (extablish connection + buffered communication) and 2 (object representation of uC) next to 0 (packets and headers)
 - output buffer is now contiusly send, with optional legacy mode
 - input buffer can now tell is number of free slots

### Fixed
 - output buffer now behaves the same as the input buffer
 - error packets and normal packets are send via functions


## [0.1.0] - 2023-01-25

### Added 
- all commands can be timed with ~100us presision (modifiable)
- all interfaces are dynamicly set up by API on runtime (no seperate firmare for different chips)
- set pin high/low
- send SPI word 8/32 bits
- send 4 phase HS word 0-32bit
- record pin change with time stamp
- read SPI word 8/32 bits with time stamp
- read 4 phase HS word 0-32bit with time stamp
- primitive packet python API
