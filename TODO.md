A list of planned extensions:

- [wontfix] fast direct access pin hardcoded AER interface 1 in and 1 out (maybe start with one)
- [x] automatic sending of output buffer as defalt (with turning off)
- [ ] AER event mapping system in the dynamic allocated RAM 500KB
- [ ] extend mapping system to be able to send pin pulses (probably needs small extra ring buffer)
- [x] expose arduino I2C interfaces
- [x] objectify the Interface_spi, Interface_pin and rename them to start with capital letter
- [x] move the isr_helper into the corresponding interface helpers
- [x] delete constance.h 
- [ ] 2 phase AER
- [ ] to speed up the AER exec implement the handshake variants as sub classesc with method overwriting so that we have less if else
- [ ] implement deactivation of interfaces and freeing pins - only full reset possible as of now.
- [x] implement additional SPI 32 bit transfer as supported by Tennsy API
- [x] make the SPI interface modes and speeds configurable via API
- [x] unify SPI 8 and 32 into SPI with width config, reuse packet addresses for I2C (remove data8 packet?)
- [ ] hand down optional headers for error messages, remove switches