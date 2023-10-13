# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Fixed

### Changed

### Removed

### Deprecated

## [0.9.0] - 2023-10-13

### Added 
 - all executions are acklogage with timestamp to the PC
 - added support for Teensy 4.0 (MIMXR)
 - added support for Arduino Zero, MRKZero and arduino MRK series (SAMD21), timed release does not work yet (trigger)
 - added software reset for UC
 - added python api level 1 (extablish connection + buffered communication) 
 - added python api level 2 (object representation of uC) next to 0 (packets and headers)
 - output buffer is now contiusly send, with optional legacy mode
 - input buffer can now tell is number of free slots
 - python can now be imported like a package
 - I2C interfaces mow available
 - added level 0 api for mapper (not functional) 
 - documentation website https://olerichter.github.io/uC-chip-interface

### Fixed
 - output buffer now behaves the same as the input buffer
 - readout now stalls data aquisition on full buffer (with warning) instead of going unresponcive

### Changed
 - error packets and normal packets are send via functions
 - SPI now can send 1-4 bytes
 - SPI can now configure mode and speed
 - Pin result is now also indicated by packet header for mapping

### Removed
 - special pin conf ackloage package 

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
