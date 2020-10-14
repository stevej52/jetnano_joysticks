#!/usr/bin/env python
"""
Pymodbus Synchronous Server Example
--------------------------------------------------------------------------

The synchronous server is implemented in pure python without any third
party libraries (unless you need to use the serial protocols which require
pyserial). This is helpful in constrained or old environments where using
twisted is just not feasible. What follows is an example of its use:
"""
# --------------------------------------------------------------------------- #
# import the various server implementations
# --------------------------------------------------------------------------- #
from pymodbus.server.sync import StartTcpServer
from pymodbus.server.sync import StartTlsServer
from pymodbus.server.sync import StartUdpServer
from pymodbus.server.sync import StartSerialServer
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSparseDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext

from pymodbus.transaction import ModbusRtuFramer, ModbusBinaryFramer
# --------------------------------------------------------------------------- #
# configure the service logging
# --------------------------------------------------------------------------- #
import logging
#FORMAT = ('%(asctime)-15s %(threadName)-15s'
#         ' %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
#logging.basicConfig(format=FORMAT)
#log = logging.getLogger()
#log.setLevel(logging.DEBUG)


def decode_client():
    client = ModbusClient('192.168.50.147', port=502)
    client.connect()
    result = client.read_holding_registers(128, 4, unit=1)

    print("Registers")
    print("-" * 60)
    print(result.registers)
    print("\n")
    decoder = BinaryPayloadDecoder.fromRegisters(result.registers,
                                                 byteorder=bo,
                                                 wordorder=wo)

    assert decoder._byteorder == builder._byteorder, \
            "Make sure byteorder is consistent between BinaryPayloadBuilder and BinaryPayloadDecoder"

    assert decoder._wordorder == builder._wordorder, \
            "Make sure wordorder is consistent between BinaryPayloadBuilder and BinaryPayloadDecoder"


    decoded = OrderedDict([
        ('string', decoder.decode_string(len(strng))),
        ('bits', decoder.decode_bits()),
        ('8int', decoder.decode_8bit_int()),
        ('8uint', decoder.decode_8bit_uint()),
        ('16int', decoder.decode_16bit_int()),
        ('16uint', decoder.decode_16bit_uint()),
        ('32int', decoder.decode_32bit_int()),
        ('32uint', decoder.decode_32bit_uint()),
        ('16float', decoder.decode_16bit_float()),
        ('16float2', decoder.decode_16bit_float()),
        ('32float', decoder.decode_32bit_float()),
        ('32float2', decoder.decode_32bit_float()),
        ('64int', decoder.decode_64bit_int()),
        ('64uint', decoder.decode_64bit_uint()),
        ('ignore', decoder.skip_bytes(8)),
        ('64float', decoder.decode_64bit_float()),
        ('64float2', decoder.decode_64bit_float()),
    ])

    print("-" * 60)
    print("Decoded Data")
    print("-" * 60)
    for name, value in iteritems(decoded):
        print("%s\t" % name, hex(value) if isinstance(value, int) else value)
def run_server():
    # ----------------------------------------------------------------------- #
    # initialize your data store
    # ----------------------------------------------------------------------- #
    # The datastores only respond to the addresses that they are initialized to
    # Therefore, if you initialize a DataBlock to addresses of 0x00 to 0xFF, a
    # request to 0x100 will respond with an invalid address exception. This is
    # because many devices exhibit this kind of behavior (but not all)::
    #
    #     block = ModbusSequentialDataBlock(0x00, [0]*0xff)
    #
    # Continuing, you can choose to use a sequential or a sparse DataBlock in
    # your data context.  The difference is that the sequential has no gaps in
    # the data while the sparse can. Once again, there are devices that exhibit
    # both forms of behavior::
    #
    #     block = ModbusSparseDataBlock({0x00: 0, 0x05: 1})
    #     block = ModbusSequentialDataBlock(0x00, [0]*5)
    #
    # Alternately, you can use the factory methods to initialize the DataBlocks
    # or simply do not pass them to have them initialized to 0x00 on the full
    # address range::
    #
    #     store = ModbusSlaveContext(di = ModbusSequentialDataBlock.create())
    #     store = ModbusSlaveContext()
    #
    # Finally, you are allowed to use the same DataBlock reference for every
    # table or you may use a separate DataBlock for each table.
    # This depends if you would like functions to be able to access and modify
    # the same data or not::
    #
    #     block = ModbusSequentialDataBlock(0x00, [0]*0xff)
    #     store = ModbusSlaveContext(di=block, co=block, hr=block, ir=block)
    #
    # The server then makes use of a server context that allows the server to
    # respond with different slave contexts for different unit ids. By default
    # it will return the same context for every unit id supplied (broadcast
    # mode).
    # However, this can be overloaded by setting the single flag to False and
    # then supplying a dictionary of unit id to context mapping::
    #
    #     slaves  = {
    #         0x01: ModbusSlaveContext(...),
    #         0x02: ModbusSlaveContext(...),
    #         0x03: ModbusSlaveContext(...),
    #     }
    #     context = ModbusServerContext(slaves=slaves, single=False)
    #
    # The slave context can also be initialized in zero_mode which means that a
    # request to address(0-7) will map to the address (0-7). The default is
    # False which is based on section 4.4 of the specification, so address(0-7)
    # will map to (1-8)::
    #
    #     store = ModbusSlaveContext(..., zero_mode=True)
    # ----------------------------------------------------------------------- #
    # store = ModbusSlaveContext(
        # di=ModbusSequentialDataBlock(0, [17]*100),
        # co=ModbusSequentialDataBlock(0, [17]*100),
        # hr=ModbusSequentialDataBlock(0, [17]*100),
        # ir=ModbusSequentialDataBlock(0, [17]*100))
    store = ModbusSlaveContext(di = ModbusSequentialDataBlock.create())
    store = ModbusSlaveContext()
    context = ModbusServerContext(slaves=store, single=True)

    # ----------------------------------------------------------------------- #
    # initialize the server information
    # ----------------------------------------------------------------------- #
    # If you don't set this or any fields, they are defaulted to empty strings.
    # ----------------------------------------------------------------------- #
    identity = ModbusDeviceIdentification()
    identity.VendorName = 'Pymodbus'
    identity.ProductCode = 'PM'
    identity.VendorUrl = 'http://github.com/riptideio/pymodbus/'
    identity.ProductName = 'Pymodbus Server'
    identity.ModelName = 'Pymodbus Server'
    identity.MajorMinorRevision = '2.3.0'

    # ----------------------------------------------------------------------- #
    # run the server you want
    # ----------------------------------------------------------------------- #
    # Tcp:
    StartTcpServer(context, identity=identity, address=("", 502))
 
#    decode_client()


    #
    # TCP with different framer
    # StartTcpServer(context, identity=identity,
    #                framer=ModbusRtuFramer, address=("0.0.0.0", 5020))

    # TLS
    # StartTlsServer(context, identity=identity, certfile="server.crt",
    #                keyfile="server.key", address=("0.0.0.0", 8020))

    # Udp:
    # StartUdpServer(context, identity=identity, address=("0.0.0.0", 5020))

    # socat -d -d PTY,link=/tmp/ptyp0,raw,echo=0,ispeed=9600 PTY,link=/tmp/ttyp0,raw,echo=0,ospeed=9600
    # Ascii:
    # StartSerialServer(context, identity=identity,
    #                    port='/dev/ttyp0', timeout=1)

    # RTU:
    # StartSerialServer(context, framer=ModbusRtuFramer, identity=identity,
    #                   port='/tmp/ttyp0', timeout=.005, baudrate=9600)

    # Binary
    # StartSerialServer(context,
    #                   identity=identity,
    #                   framer=ModbusBinaryFramer,
    #                   port='/dev/ttyp0',
    #                   timeout=1)


if __name__ == "__main__":
        print("Modbus Server Running...")
        run_server()
        
