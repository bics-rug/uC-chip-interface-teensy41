A list of planned extensions:

- [ ] fast direct access pin hardcoded AER interface 1 in and 1 out (maybe start with one)
- [ ] automatic sending of output buffer as defalt (with turning off)
- [ ] AER event mapping system in the dynamic allocated RAM 500KB
- [ ] extend mapping system to be able to send pin pulses (probably needs small extra ring buffer)
- [ ] expose arduino I2C interfaces
- [ ] objectify the spi_helper, pin_helper and rename them to start with capital letter
- [ ] move the isr_helper into the corresponding interface helpers
- [x] delete constance.h 
- [ ] 2 phase AER
- [ ] to speed up the AER exec implement the handshake variants as sub classesc with method overwriting so that we have less if else
- [ ] implement deactivation of interfaces and freeing pins 
- [x] implement additional SPI 32 bit transfer as supported by Tennsy API
- [ ] make the SPI interface modes and speeds configurable via API