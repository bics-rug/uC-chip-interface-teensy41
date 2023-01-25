# uC chip interface for async/neuromorphic test chips

the purpose of this firmware is to have an easy interface from the PC to a test chip:

the following functions are currently availible:

- all commands can be timed with ~100us presision (modifiable)
- all interfaces are dynamicly set up by API on runtime (no seperate firmare for different chips)
- set pin high/low
- send SPI word 8/32 bits
- send 4 phase HS word 0-32bit
- record pin change with time stamp
- read SPI word 8/32 bits with time stamp
- read 4 phase HS word 0-32bit with time stamp
- primitive python API

for planned additions see TODO.md

## how to contribute

contributions are very wellcome, please reach out and/or open a pull request!

it would help us and your pull request if you add code/function docs and ideally if it makes sense a test/example, 
please note down your changes in CHANGELOG.md below [Unreleased].

@people with direct repo access, do not commit to main or dev directly do feature branches and pull requests! 

all chip specific files and higher level APIs should be in thier own seperate repos
