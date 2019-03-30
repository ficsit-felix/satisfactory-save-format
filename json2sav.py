#!/usr/bin/env python3
"""
Converts from the more readable format (.json) back to a Satisfactory save game (.sav)
"""

import struct
import json
import argparse
import pathlib
import sys

parser = argparse.ArgumentParser(
    description='Converts from the more readable format back to a Satisfactory save game')
parser.add_argument('file', metavar='FILE', type=str,
                    help='json file to process')
parser.add_argument('--output', '-o', type=str, help='output file (.sav)')
args = parser.parse_args()

extension = pathlib.Path(args.file).suffix
if extension == '.sav':
    print('error: extension of save file should be .json', file=sys.stderr)
    exit(1)

f = open(args.file, 'r')
saveJson = json.loads(f.read())

if args.output == None:
    output_file = pathlib.Path(args.file).stem + '.sav'
else:
    output_file = args.output

output = open(output_file, 'wb')


buffers = []


def write(bytes, count=True):
    if len(buffers) == 0:
        output.write(bytes)
    else:
        buffers[len(buffers)-1]['buffer'].append(bytes)
        if count:
            buffers[len(buffers)-1]['length'] += len(bytes)


def addBuffer():
    """
    pushes a new buffer to the stack, so that the length of the following content can be written before the content
    """
    buffers.append({'buffer': [], 'length': 0})


def endBufferAndWriteSize():
    """
    ends the top buffer and writes it's context prefixed by the length (possibly into another buffer)
    """
    buffer = buffers[len(buffers)-1]
    buffers.remove(buffer)
    # writeInt(26214) # TODO length
    writeInt(buffer['length'])
    for b in buffer['buffer']:
        write(b)
    return buffer['length']


def assertFail(message):
    print('failed: ' + message)
    input()
    assert False


def writeInt(value, count=True):
    write(struct.pack('i', value), count)


def writeFloat(value):
    write(struct.pack('f', value))


def writeLong(value):
    write(struct.pack('q', value))


def writeByte(value, count=True):
    write(struct.pack('b', value), count)


def writeLengthPrefixedString(value, count=True):
    if len(value) == 0:
        writeInt(0, count)
        return
    writeInt(len(value)+1, count)
    for i in value:
        write(struct.pack('b', ord(i)), count)
    write(b'\x00', count)


def writeHex(value, count=True):
    write(bytearray.fromhex(value), count)


# Header
writeInt(saveJson['saveHeaderType'])
writeInt(saveJson['saveVersion'])
writeInt(saveJson['buildVersion'])
writeLengthPrefixedString(saveJson['mapName'])
writeLengthPrefixedString(saveJson['mapOptions'])
writeLengthPrefixedString(saveJson['sessionName'])
writeInt(saveJson['playDurationSeconds'])
writeLong(saveJson['saveDateTime'])
writeByte(saveJson['sessionVisibility'])

writeInt(len(saveJson['objects']))


def writeActor(obj):
    writeLengthPrefixedString(obj['className'])
    writeLengthPrefixedString(obj['levelName'])
    writeLengthPrefixedString(obj['pathName'])
    writeInt(obj['needTransform'])
    writeFloat(obj['transform']['rotation'][0])
    writeFloat(obj['transform']['rotation'][1])
    writeFloat(obj['transform']['rotation'][2])
    writeFloat(obj['transform']['rotation'][3])
    writeFloat(obj['transform']['translation'][0])
    writeFloat(obj['transform']['translation'][1])
    writeFloat(obj['transform']['translation'][2])
    writeFloat(obj['transform']['scale3d'][0])
    writeFloat(obj['transform']['scale3d'][1])
    writeFloat(obj['transform']['scale3d'][2])
    writeInt(obj['wasPlacedInLevel'])


def writeObject(obj):
    writeLengthPrefixedString(obj['className'])
    writeLengthPrefixedString(obj['levelName'])
    writeLengthPrefixedString(obj['pathName'])
    writeLengthPrefixedString(obj['outerPathName'])


for obj in saveJson['objects']:
    writeInt(obj['type'])
    if obj['type'] == 1:
        writeActor(obj)
    elif obj['type'] == 0:
        writeObject(obj)
    else:
        assertFail('unknown type ' + str(type))

writeInt(len(saveJson['objects']))


def writeProperty(property):
    writeLengthPrefixedString(property['name'])
    type = property['type']
    writeLengthPrefixedString(type)
    addBuffer()
    writeInt(0, count=False)
    if type == 'IntProperty':
        writeByte(0, count=False)
        writeInt(property['value'])
    elif type == 'BoolProperty':
        writeByte(property['value'], count=False)
        writeByte(0, count=False)
    elif type == 'FloatProperty':
        writeByte(0, count=False)
        writeFloat(property['value'])
    elif type == 'StrProperty':
        writeByte(0, count=False)
        writeLengthPrefixedString(property['value'])
    elif type == 'NameProperty':
        writeByte(0, count=False)
        writeLengthPrefixedString(property['value'])
    elif type == 'TextProperty':
        writeByte(0, count=False)
        writeHex(property['textUnknown'])
        writeLengthPrefixedString(property['value'])
    elif type == 'ByteProperty':  # TODO

        writeLengthPrefixedString(property['value']['unk1'], count=False)
        if property['value']['unk1'] == 'EGamePhase':
            writeByte(0, count=False)
            writeLengthPrefixedString(property['value']['unk2'])
        else:
            writeByte(0, count=False)
            writeByte(property['value']['unk2'])
    elif type == 'EnumProperty':
        writeLengthPrefixedString(property['value']['enum'], count=False)
        writeByte(0, count=False)
        writeLengthPrefixedString(property['value']['value'])
    elif type == 'ObjectProperty':
        writeByte(0, count=False)
        writeLengthPrefixedString(property['value']['levelName'])
        writeLengthPrefixedString(property['value']['pathName'])

    elif type == 'StructProperty':
        writeLengthPrefixedString(property['value']['type'], count=False)
        writeHex(property['structUnknown'], count=False)

        type = property['value']['type']
        if type == 'Vector' or type == 'Rotator':
            writeFloat(property['value']['x'])
            writeFloat(property['value']['y'])
            writeFloat(property['value']['z'])
        elif type == 'Box':
            writeFloat(property['value']['min'][0])
            writeFloat(property['value']['min'][1])
            writeFloat(property['value']['min'][2])
            writeFloat(property['value']['max'][0])
            writeFloat(property['value']['max'][1])
            writeFloat(property['value']['max'][2])
            writeByte(property['value']['isValid'])
        elif type == 'LinearColor':
            writeFloat(property['value']['r'])
            writeFloat(property['value']['g'])
            writeFloat(property['value']['b'])
            writeFloat(property['value']['a'])
        elif type == 'Transform':
            for prop in property['value']['properties']:
                writeProperty(prop)
            writeNone()
        elif type == 'Quat':
            writeFloat(property['value']['a'])
            writeFloat(property['value']['b'])
            writeFloat(property['value']['c'])
            writeFloat(property['value']['d'])
        elif type == 'RemovedInstanceArray' or type == 'InventoryStack':
            for prop in property['value']['properties']:
                writeProperty(prop)
            writeNone()
        elif type == 'InventoryItem':
            writeLengthPrefixedString(property['value']['unk1'], count=False)
            writeLengthPrefixedString(property['value']['itemName'])
            writeLengthPrefixedString(property['value']['levelName'])
            writeLengthPrefixedString(property['value']['pathName'])
            oldval = buffers[len(buffers)-1]['length']
            writeProperty(property['value']['properties'][0])
            # Dirty hack to make in this one case the inner property only take up 4 bytes
            buffers[len(buffers)-1]['length'] = oldval + 4

    elif type == 'ArrayProperty':
        itemType = property['value']['type']
        writeLengthPrefixedString(itemType, count=False)
        writeByte(0, count=False)
        writeInt(len(property['value']['values']))
        if itemType == 'IntProperty':
            for obj in property['value']['values']:
                writeInt(obj)
        elif itemType == 'ObjectProperty':
            for obj in property['value']['values']:
                writeLengthPrefixedString(obj['levelName'])
                writeLengthPrefixedString(obj['pathName'])
        elif itemType == 'StructProperty':
            writeLengthPrefixedString(property['structName'])
            writeLengthPrefixedString(property['structType'])
            addBuffer()
            writeInt(0, count=False)
            writeLengthPrefixedString(property['structInnerType'], count=False)
            writeHex(property['structUnknown'], count=False)
            for obj in property['value']['values']:
                for prop in obj['properties']:
                    writeProperty(prop)
                writeNone()
            structLength = endBufferAndWriteSize()
            if (structLength != property['_structLength']):
                print('struct: ' + str(structLength) +
                      '/' + str(property['_structLength']))
                print(json.dumps(property, indent=4))
    elif type == 'MapProperty':
        writeLengthPrefixedString(property['value']['name'], count=False)
        writeLengthPrefixedString(property['value']['type'], count=False)
        writeByte(0, count=False)
        writeInt(0)  # for some reason this counts towards the length

        writeInt(len(property['value']['values']))
        for key, value in property['value']['values'].items():
            writeInt(int(key))
            for prop in value:
                writeProperty(prop)
            writeNone()
    length = endBufferAndWriteSize()
    if (length != property['_length']):
        print(str(length) + '/' + str(property['_length']))
        print(json.dumps(property, indent=4))


def writeNone():
    writeLengthPrefixedString('None')


def writeEntity(withNames, obj):
    addBuffer()  # size will be written at this place later
    if withNames:
        writeLengthPrefixedString(obj['levelName'])
        writeLengthPrefixedString(obj['pathName'])
        writeInt(len(obj['children']))
        for child in obj['children']:
            writeLengthPrefixedString(child['levelName'])
            writeLengthPrefixedString(child['pathName'])

    for property in obj['properties']:
        writeProperty(property)
    writeNone()

    writeHex(obj['missing'])
    endBufferAndWriteSize()


for obj in saveJson['objects']:
    if obj['type'] == 1:
        writeEntity(True, obj['entity'])
    elif obj['type'] == 0:
        writeEntity(False, obj['entity'])

writeHex(saveJson['missing'])
