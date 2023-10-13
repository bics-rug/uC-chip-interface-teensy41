# The PC <--usb--> uC protocol

The communication happens via a USB serial connection. The communication protocol is handled via fixed-length 9-byte packages @ref packet_t, where the first byte is the header, which specifies the data format of the following 8 bytes, and the next 4 bytes (except for the error packets) are a timestamp in microseconds, leaving the last 4 bytes for data. In detail, the following data formats exist:
 - @ref data32_t , @ref uC_api.packet.Data32bitPacket "Data32bitPacket" using the headers listed in @ref uC_api.header.Data32bitHeader "Data32bitHeader" 
    ```
    [header: 1 byte][time: 4 byte][value: 4 byte]
    ```
 - @ref data_i2c_t , @ref uC_api.packet.DataI2CPacket "DataI2CPacket" using the headers listed in @ref uC_api.header.DataI2CHeader "DataI2CHeader" 
    ```
    [header : 1 byte][time: 4 byte][address: 7 bit][R/W: 1 bit][Reg Address: 1 byte][value: 2 byte]
    ```
 - @ref pin_t , @ref uC_api.packet.PinPacket "PinPacket" using the headers listed in @ref uC_api.header.PinHeader "PinHeader" 
    ```
    [header : 1 byte][time: 4 byte][Pin number: 1 byte][value: 1 byte][not used: 2 byte]
    ```
 - @ref config_t , @ref uC_api.packet.ConfigPacket "ConfigPacket" using the headers listed in @ref uC_api.header.ConfigMainHeader "ConfigMainHeader" and the sub-headers in @ref uC_api.header.ConfigSubHeader "ConfigSubHeader" 
    ```
    [header : 1 byte][time: 4 byte][config header: 1 byte][value: 1 byte][not used: 2 byte]
    ```
 - @ref error_t , @ref uC_api.packet.ErrorPacket "ErrorPacket" using the headers listed in @ref uC_api.header.ErrorHeader "ErrorHeader" 
    ```
    [header : 1 byte][causing header: 1 byte][value: 4 byte][causing sub header: 1 byte][not used: 2 byte]
    ```