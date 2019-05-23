#!/usr/bin/env python3
"""
Converts Satisfactory save games (.sav) into a more readable format (.json)
"""
import struct
import functools
import itertools
import csv
import binascii
import sys
import json
import argparse
import pathlib

parser = argparse.ArgumentParser(
    description='Converts Satisfactory save games into a more readable format')
parser.add_argument('file', metavar='FILE', type=str,
                    help='save game to process (.sav file extension)')
parser.add_argument('--output', '-o', type=str, help='output file (.json)')
parser.add_argument('--pretty', '-p', help='pretty print json', action='store_true')

args = parser.parse_args()

extension = pathlib.Path(args.file).suffix
if extension != '.sav':
    print('error: extension of save file should be .sav', file=sys.stderr)
    exit(1)

f = open(args.file, 'rb')

# determine the file size so that we can
f.seek(0, 2)
fileSize = f.tell()
f.seek(0, 0)

bytesRead = 0


def assertFail(message):
    print('assertion failed: ' + message, file=sys.stderr)
    # show the next bytes to help debugging
    print(readHex(32))
    input()
    assert False


def readInt():
    global bytesRead
    bytesRead += 4
    return struct.unpack('i', f.read(4))[0]


def readFloat():
    global bytesRead
    bytesRead += 4
    return struct.unpack('f', f.read(4))[0]


def readLong():
    global bytesRead
    bytesRead += 8
    return struct.unpack('q', f.read(8))[0]


def readByte():
    global bytesRead
    bytesRead += 1
    return struct.unpack('b', f.read(1))[0]


def assertNullByte():
    global bytesRead
    bytesRead += 1
    zero = f.read(1)
    if zero != b'\x00':
        assertFail('not null but ' + str(zero))


def readLengthPrefixedString():
    """
    Reads a string that is prefixed with its length
    """
    global bytesRead
    length = readInt()
    if length == 0:
        return ''
    
    if length < 0:
        # Read UTF-16
        length = length * -2
        
        chars = f.read(length-2)

        zero = f.read(2)
        bytesRead += length

        if zero != b'\x00\x00':  # We assume that the last byte of a string is alway \x00\x00
            if length > 100:
                assertFail('zero is ' + str(zero) + ' in ' + str(chars[0:100]))
            else:
                assertFail('zero is ' + str(zero) + ' in ' + str(chars))
        return chars.decode('utf-16')

    # Read ASCII
        
    chars = f.read(length-1)

    zero = f.read(1)
    bytesRead += length

    if zero != b'\x00':  # We assume that the last byte of a string is alway \x00
        if length > 100:
            assertFail('zero is ' + str(zero) + ' in ' + str(chars[0:100]))
        else:
            assertFail('zero is ' + str(zero) + ' in ' + str(chars))
    return chars.decode('ascii')

def readHex(count):
    """
    Reads count bytes and returns their hex form
    """
    global bytesRead
    bytesRead += count

    chars = f.read(count)
    c = 0
    result = ''
    for i in chars:
        result += format(i, '02x') + ' '
        c += 1
        if (c % 4 == 0 and c < count - 1):
            result += ' '

    return result


# Read the file header
saveHeaderType = readInt()
saveVersion = readInt()  # Save Version
buildVersion = readInt()  # BuildVersion

mapName = readLengthPrefixedString()  # MapName
mapOptions = readLengthPrefixedString()  # MapOptions
sessionName = readLengthPrefixedString()  # SessionName
playDurationSeconds = readInt()  # PlayDurationSeconds

saveDateTime = readLong()  # SaveDateTime
'''
to convert this FDateTime to a unix timestamp use:
saveDateSeconds = saveDateTime / 10000000
# see https://stackoverflow.com/a/1628018
print(saveDateSeconds-62135596800)
'''
sessionVisibility = readByte()  # SessionVisibility

entryCount = readInt()  # total entries
saveJson = {
    'saveHeaderType': saveHeaderType,
    'saveVersion': saveVersion,
    'buildVersion': buildVersion,
    'mapName': mapName,
    'mapOptions': mapOptions,
    'sessionName': sessionName,
    'playDurationSeconds': playDurationSeconds,
    'saveDateTime': saveDateTime,
    'sessionVisibility': sessionVisibility,
    'objects': [],
    'collected': []
}


def readActor():
    className = readLengthPrefixedString()
    levelName = readLengthPrefixedString()
    pathName = readLengthPrefixedString()
    needTransform = readInt()

    a = readFloat()
    b = readFloat()
    c = readFloat()
    d = readFloat()
    x = readFloat()
    y = readFloat()
    z = readFloat()
    sx = readFloat()
    sy = readFloat()
    sz = readFloat()

    wasPlacedInLevel = readInt()

    return {
        'type': 1,
        'className': className,
        'levelName': levelName,
        'pathName': pathName,
        'needTransform': needTransform,
        'transform': {
            'rotation': [a, b, c, d],
            'translation': [x, y, z],
            'scale3d': [sx, sy, sz],

        },
        'wasPlacedInLevel': wasPlacedInLevel
    }


def readObject():
    className = readLengthPrefixedString()
    levelName = readLengthPrefixedString()
    pathName = readLengthPrefixedString()
    outerPathName = readLengthPrefixedString()

    return {
        'type': 0,
        'className': className,
        'levelName': levelName,
        'pathName': pathName,
        'outerPathName': outerPathName
    }


for i in range(0, entryCount):
    type = readInt()
    if type == 1:
        saveJson['objects'].append(readActor())
    elif type == 0:
        saveJson['objects'].append(readObject())
    else:
        assertFail('unknown type ' + str(type))


elementCount = readInt()

# So far these counts have always been the same and the entities seem to belong 1 to 1 to the actors/objects read above
if elementCount != entryCount:
    assertFail('elementCount ('+str(elementCount) +
               ') != entryCount('+str(entryCount)+')')


def readProperty(properties):
    name = readLengthPrefixedString()
    if name == 'None':
        return

    prop = readLengthPrefixedString()
    length = readInt()
    index = readInt()

    property = {
        'name': name,
        'type': prop,
        '_length': length,
        'index': index
    }

    if prop == 'IntProperty':
        assertNullByte()
        property['value'] = readInt()

    elif prop == 'StrProperty':
        assertNullByte()
        property['value'] = readLengthPrefixedString()

    elif prop == 'StructProperty':
        type = readLengthPrefixedString()

        property['structUnknown'] = readHex(17)  # TODO

        if type == 'Vector' or type == 'Rotator':
            x = readFloat()
            y = readFloat()
            z = readFloat()
            property['value'] = {
                'type': type,
                'x': x,
                'y': y,
                'z': z
            }
                    
        elif type == 'Box':
            minX = readFloat()
            minY = readFloat()
            minZ = readFloat()
            maxX = readFloat()
            maxY = readFloat()
            maxZ = readFloat()
            isValid = readByte()
            property['value'] = {
                'type': type,
                'min': [minX, minY, minZ],
                'max': [maxX, maxY, maxZ],
                'isValid': isValid
            }
        elif type == 'LinearColor':
            r = readFloat()
            g = readFloat()
            b = readFloat()
            a = readFloat()
            property['value'] = {
                'type': type,
                'r': r,
                'g': g,
                'b': b,
                'a': a
            }
        elif type == 'Transform':
            props = []
            while (readProperty(props)):
                pass
            property['value'] = {
                'type': type,
                'properties': props
            }

        elif type == 'Quat':
            a = readFloat()
            b = readFloat()
            c = readFloat()
            d = readFloat()
            property['value'] = {
                'type': type,
                'a': a,
                'b': b,
                'c': c,
                'd': d
            }

        elif type == 'RemovedInstanceArray' or type == 'InventoryStack':
            props = []
            while (readProperty(props)):
                pass
            property['value'] = {
                'type': type,
                'properties': props
            }
        elif type == 'InventoryItem':
            unk1 = readLengthPrefixedString()  # TODO
            itemName = readLengthPrefixedString()
            levelName = readLengthPrefixedString()
            pathName = readLengthPrefixedString()

            props = []
            readProperty(props)
            # can't consume null here because it is needed by the entaingling struct

            property['value'] = {
                'type': type,
                'unk1': unk1,
                'itemName': itemName,
                'levelName': levelName,
                'pathName': pathName,
                'properties': props
            }
        elif type == 'Color':
            a = readHex(1)
            b = readHex(1)
            c = readHex(1)
            d = readHex(1)
            property['value'] = {
                'type': type,
            	'r': a,
            	'g': b,
            	'b': c,
            	'a': d
            }
        else:
            assertFail('Unknown type: ' + type)

    elif prop == 'ArrayProperty':
        itemType = readLengthPrefixedString()
        assertNullByte()
        count = readInt()
        values = []

        if itemType == 'ObjectProperty':
            for j in range(0, count):
                values.append({
                    'levelName': readLengthPrefixedString(),
                    'pathName': readLengthPrefixedString()
                })
        elif itemType == 'StructProperty':
            structName = readLengthPrefixedString()
            structType = readLengthPrefixedString()
            structSize = readInt()
            zero = readInt()
            if zero != 0:
                assertFail('not zero: ' + str(zero))

            type = readLengthPrefixedString()

            property['structName'] = structName
            property['structType'] = structType
            property['structInnerType'] = type

            property['structUnknown'] = readHex(17)  # TODO what are those?
            property['_structLength'] = structSize
            for i in range(0, count):
                props = []
                while (readProperty(props)):
                    pass
                values.append({
                    'properties': props
                })

        elif itemType == 'IntProperty':
            for i in range(0, count):
                values.append(readInt())

        elif itemType == 'ByteProperty':
            for i in range(0, count):
                values.append(readByte())

        else:
            assertFail('unknown itemType ' + itemType + ' in name ' + name)

        property['value'] = {
            'type': itemType,
            'values': values
        }
    elif prop == 'ObjectProperty':
        assertNullByte()
        property['value'] = {
            'levelName': readLengthPrefixedString(),
            'pathName': readLengthPrefixedString()
        }
    elif prop == 'BoolProperty':
        property['value'] = readByte()
        assertNullByte()
    elif prop == 'FloatProperty':  # TimeStamps that are FloatProperties are negative to the current time in seconds?
        assertNullByte()
        property['value'] = readFloat()
    elif prop == 'EnumProperty':
        enumName = readLengthPrefixedString()
        assertNullByte()
        valueName = readLengthPrefixedString()
        property['value'] = {
            'enum': enumName,
            'value': valueName,
        }
    elif prop == 'NameProperty':
        assertNullByte()
        property['value'] = readLengthPrefixedString()
    elif prop == 'MapProperty':
        name = readLengthPrefixedString()
        valueType = readLengthPrefixedString()
        for i in range(0, 5):
            assertNullByte()
        count = readInt()
        values = {
        }
        for i in range(0, count):
            key = readInt()
            props = []
            while readProperty(props):
                pass
            values[key] = props

        property['value'] = {
            'name': name,
            'type': valueType,
            'values': values
        }
    elif prop == 'ByteProperty':  # TODO

        unk1 = readLengthPrefixedString()  # TODO
        if unk1 == 'None':
            assertNullByte()
            property['value'] = {
                'unk1': unk1,
                'unk2': readByte()
            }
        else:
            assertNullByte()
            unk2 = readLengthPrefixedString()  # TODO
            property['value'] = {
                'unk1': unk1,
                'unk2': unk2
            }
        
    elif prop == 'TextProperty':
        assertNullByte()
        property['textUnknown'] = readHex(13)  # TODO
        property['value'] = readLengthPrefixedString()
    else:
        assertFail('Unknown property type: ' + prop)

    properties.append(property)
    return True


def readEntity(withNames, length):
    global bytesRead
    bytesRead = 0

    entity = {}

    if withNames:
        entity['levelName'] = readLengthPrefixedString()
        entity['pathName'] = readLengthPrefixedString()
        entity['children'] = []

        childCount = readInt()
        if childCount > 0:
            for i in range(0, childCount):
                levelName = readLengthPrefixedString()
                pathName = readLengthPrefixedString()
                entity['children'].append({
                    'levelName': levelName,
                    'pathName': pathName
                })
    entity['properties'] = []
    while (readProperty(entity['properties'])):
        pass

    # read missing bytes at the end of this entity.
    # maybe we missed something while parsing the properties?
    missing = length - bytesRead
    if missing > 0:
        entity['missing'] = readHex(missing)
    elif missing < 0:
        assertFail('negative missing amount: ' + str(missing))

    return entity


for i in range(0, elementCount):
    length = readInt()  # length of this entry
    if saveJson['objects'][i]['type'] == 1:
        saveJson['objects'][i]['entity'] = readEntity(True, length)
    else:
        saveJson['objects'][i]['entity'] = readEntity(False, length)


collectedCount = readInt()

for i in range(0, collectedCount):
    levelName = readLengthPrefixedString()
    pathName = readLengthPrefixedString()
    saveJson['collected'].append({'levelName': levelName, 'pathName': pathName})

# store the remaining bytes as well so that we can recreate the exact same save file
saveJson['missing'] = readHex(fileSize - f.tell())


if args.output == None:
    output_file = pathlib.Path(args.file).stem + '.json'
else:
    output_file = args.output
output = open(output_file, 'w')
if args.pretty == True:
    output.write(json.dumps(saveJson, indent=4))
else:
    output.write(json.dumps(saveJson))
output.close()
print('converted savegame saved to ' + output_file)
