#!/usr/bin/env python3

import struct

import functools
import itertools
import csv
import binascii
import sys
import json


def readcstr(f):
    toeof = iter(functools.partial(f.read, 1), '')
    return ''.join(itertools.takewhile(b'0'.__ne__, toeof))


f = open("big.sav", "rb")
f.seek(0, 2)
fileSize = f.tell()
f.seek(0, 0)


levelWriter = csv.writer(open('levels.csv', 'w', newline=''))
objectWriter = csv.writer(open('objects.csv', 'w', newline=''))
objectTypeWriter = csv.writer(open('objectTypes.csv', 'w', newline=''))
elementWriter = csv.writer(open('elements.csv', 'w', newline=''))
pointWriter = csv.writer(open('points.csv', 'w', newline=''))
pointWriter.writerow(['x', 'y', 'z', 'type'])


bytesRead = 0

def assertFail(message):
    print('failed: ' +message)
    readHex(32)
    input()
    assert False


def readString(myfile):
    chars = []
    while True:
        c = myfile.read(1)
        # print(c)
#        print(b'0')
        if c is None or c == b'\x00':
            return b''.join(chars).decode('ascii')
        chars.append(c)


def readLengthPrefixedString():
    global bytesRead
    length = readInt()
    # bytesRead += 4
    if length == 0:
        return ''

    chars = f.read(length-1)
    zero = f.read(1)
    bytesRead += length
    if zero != b'\x00':
        if length > 100:
            print('zero is ' + str(zero) + ' in ' + str(chars[0:100]))
        else:
            print('zero is ' + str(zero) + ' in ' + str(chars))
        assert False
    return chars.decode('ascii')


def readInt():
    global bytesRead
    bytesRead += 4
    return struct.unpack('i', f.read(4))[0]
    # return int.from_bytes(f.read(4), byteorder='little')


def readFloat():
    global bytesRead
    bytesRead += 4
    return struct.unpack('f', f.read(4))[0]


def readLong():
    global bytesRead
    bytesRead += 8
    return struct.unpack('l', f.read(8))[0]


def readByte():
    global bytesRead
    bytesRead += 1
    return struct.unpack('b', f.read(1))[0]

def assertNullByte():
    global bytesRead
    bytesRead += 1
    zero = f.read(1)
    if zero !=  b'\x00':
        assertFail('not null but ' + str(zero))

def readHex(count):
    global bytesRead
    bytesRead += count

    chars = f.read(count)
    c = 0
    result = ''
    for i in chars:
        print(format(i, '02x'), end=' ')
        result += format(i, '02x') + ' '
        c += 1
        if (c % 4 == 0):
            print('', end=' ')
            result += ' '

    print(' | ', end='')

    c = 0
    for i in chars:
        if (i > 31 and i < 128):
            print(chr(i), end='')
        else:
            print('.', end='')
        c += 1
        if (c % 4 == 0):
            print('', end=' ')
    print('')
    return result


### START OF HEADER ###
print('START OF HEADERq')
saveHeaderType = readInt()
saveVersion = readInt()  # Save Version
buildVersion = readInt()  # BuildVersion

mapName = readLengthPrefixedString()  # MapName
mapOptions = readLengthPrefixedString()  # MapOptions
sessionName = readLengthPrefixedString()  # SessionName
playDurationSeconds = readInt()  # PlayDurationSeconds

saveDateTime = readLong()  # SaveDateTime
saveDateSeconds = saveDateTime / 10000000
# see https://stackoverflow.com/a/1628018
print(saveDateSeconds-62135596800)

# print(readLong())
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
    'objects': []
}


# input()


def nprint(x):
    pass


def readLevelName():
    name = readLengthPrefixedString()
    levelWriter.writerow([name])
    print(name)
    return name


def readObjectName():
    name = readLengthPrefixedString()
    objectWriter.writerow([name])
    print(name)
    return name


def readObjectType():
    name = readLengthPrefixedString()
    objectTypeWriter.writerow([name])
    print(name)
    return name


def readActor(nr):

    className = readObjectType()
    levelName = readLevelName()
    pathName = readObjectName()
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

def readObject(nr):
    className = readObjectType()
    levelName = readLevelName()
    pathName = readObjectName()
    outerPathName = readLengthPrefixedString()

    return {
        'type': 0,
        'className': className,
        'levelName': levelName,
        'pathName': pathName,
        'outerPathName': outerPathName
    }


type0Count = 0

for i in range(0, entryCount): 
    type = readInt()
    print('type: ' + str(type))
    if type == 1:
        saveJson["objects"].append(readActor(i))
    elif type == 0:
        saveJson["objects"].append(readObject(i))
        type0Count += 1
    else:
        assertFail('unknown type ' + str(type))

print('type0Count: ' + str(type0Count))


elementCount = readInt()


def readNull():
    readHex(12)
    print(readLengthPrefixedString())
    readHex(4)


def readProperty(properties):
    name = readLengthPrefixedString()
    if name == 'None':
        print('- [None]')
        return

    prop = readLengthPrefixedString()
    length = readInt()
    zero = readInt()
    print('- ' + prop + ' ' + name + '(' + str(length)+')')
    if zero != 0:
        assertFail('not null: ' + str(zero))

    property = {
        'name': name,
        'type': prop
    }

    if prop == 'IntProperty':
        assertNullByte()
        property['value'] = readInt()
    elif prop == 'StrProperty':
        assertNullByte()
        property['value'] = readLengthPrefixedString()
    elif prop == 'StructProperty':
        type = readLengthPrefixedString()
        print('structType: ' + type)

        property['structUnknown'] = readHex(17) # TODO

        if type == 'Vector' or type == 'Rotator':
            x = readFloat()
            y = readFloat()
            z = readFloat()
            print(x)
            print(y)
            print(z)
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
                'properties' : props
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
            unk1 = readLengthPrefixedString() # TODO
            itemName = readLengthPrefixedString()
            unk2 = readLengthPrefixedString() # TODO
            unk3 = readLengthPrefixedString() # TODO
            # while readProperty():
            #   pass
            props = []
            readProperty(props)
            # can't consume null here because it might be needed by the overarching struct

            property['value'] = {
                'type': type,
                'unk1': unk1,
                'itemName': itemName,
                'unk2': unk2,
                'unk3': unk3,
                'properties': props
            }
        else:
            print('Unknown type: ' + type)
            readHex(32)
            input()
            assert False

    elif prop == 'ArrayProperty':
        itemType = readLengthPrefixedString()
        print('itemType: ' + itemType)
        assertNullByte()
        count = readInt()
        print('count: ' + str(count))
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
            print(structName + ' ' + structType + ' '+ str(structSize))
            type = readLengthPrefixedString()  # MessageData
            print(type)

            property['structName'] = structName
            property['structType'] = structType
            property['structInnerType'] = type

            property['structUnknown'] = readHex(17) # TODO what are those?

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
        else:
            print('unknown itemType ' + itemType)
            readHex(32)
            input()
            assert False

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
    elif prop == 'FloatProperty':
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
        print('count: ' + str(count))
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
    elif prop == 'ByteProperty':# TODO

        unk1 = readLengthPrefixedString()  # TODO
        print(unk1)
        if unk1 == 'EGamePhase':
            assertNullByte()
            unk2 = readLengthPrefixedString()  # TODO
            property['value'] = {
                'unk1': unk1,
                'unk2': unk2
            }
        elif unk1 == 'None':
            property['value'] = {
                'unk1': unk1,
                'unk2': readHex(2)
            }
        else:
            assertFail('unknown byte property ' + unk1)

    elif prop == 'TextProperty':
        property['textUnknown'] = readHex(14) # TODO
        property['value'] = readLengthPrefixedString()
    else:
        print('Unknown property type: ' + prop)
        readHex(32)
        input()
        assert False

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

        childCount = readInt()  # TODO maybe child count? seems to
        if childCount > 0:
#            print('children('+str(childCount)+'): [')
            for i in range(0, childCount):
                levelName = readLengthPrefixedString()
                pathName = readLengthPrefixedString()
                entity['children'].append({
                    'levelName': levelName,
                    'pathName': pathName
                })
                #print('    ' + readLengthPrefixedString())
                #print('    ' + readLengthPrefixedString())
#            print(']')

    # print('..'+ str(bytesRead))
    entity['properties'] = []
    while (readProperty(entity['properties'])):
        print('------')
        pass
    missing = length - bytesRead
    if missing > 0:
        print('$ got missing ('+str(missing)+'):')
        entity['missing'] = readHex(missing)
    elif missing < 0:
        assertFail('negative missing amount: ' + str(missing))
        

    return entity




for i in range(0, elementCount):
    length = readInt()  # TODO: might actually be length of the following entry?
    print('length: ' + str(length))

#
    # print(readLengthPrefixedString())
    # print(readLengthPrefixedString())
    # readInt()
    # readProperty()
    # readProperty()
    # readProperty()
    print(': ' + str(i))
    # sys.stdout = open('output/'+str(i)+'.txt', 'a')
    if i < elementCount - type0Count:
        saveJson['objects'][i]['entity'] = readEntity(True, length)
    else:
        saveJson['objects'][i]['entity'] = readEntity(False, length)
    # sys.stdout = sys.__stdout__
saveJson['missing'] = readHex(fileSize - f.tell())
print('finished')

output = open('output.json', 'w')
output.write(json.dumps(saveJson, indent=4))
output.close()
print('done')