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


levelWriter = csv.writer(open('levels.csv', 'w', newline=''))
objectWriter = csv.writer(open('objects.csv', 'w', newline=''))
objectTypeWriter = csv.writer(open('objectTypes.csv', 'w', newline=''))
elementWriter = csv.writer(open('elements.csv', 'w', newline=''))
pointWriter = csv.writer(open('points.csv', 'w', newline=''))
pointWriter.writerow(['x', 'y', 'z', 'type'])


bytesRead = 0

def assertFail(message):
    print('failed: ' +message)
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
        assertFail('not null but ' + zero)

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
'''
              - LF_MEMBER [name = `FileTypeTag`, Type = 0x0074 (int), offset = 0, attrs = public]
              - LF_MEMBER [name = `SaveGameFileVersion`, Type = 0x0074 (int), offset = 4, attrs = public]
              - LF_MEMBER [name = `PackageFileUE4Version`, Type = 0x0074 (int), offset = 8, attrs = public]
              - LF_MEMBER [name = `SavedEngineVersion`, Type = 0x7665, offset = 16, attrs = public]
              - LF_MEMBER [name = `CustomVersionFormat`, Type = 0x0074 (int), offset = 48, attrs = public]
              - LF_MEMBER [name = `CustomVersions`, Type = 0x26D7, offset = 56, attrs = public]
              - LF_MEMBER [name = `SaveGameClassName`, Type = 0x102E, offset = 72, attrs = public]
'''

'''
              - LF_METHOD [name = `FSaveHeader`, # overloads = 4, overload list = 0xEDCD4]
              - LF_MEMBER [name = `SaveVersion`, Type = 0x0074 (int), offset = 0, attrs = public]
              - LF_MEMBER [name = `BuildVersion`, Type = 0x0074 (int), offset = 4, attrs = public]
              - LF_MEMBER [name = `SaveName`, Type = 0x102E, offset = 8, attrs = public]
              - LF_MEMBER [name = `MapName`, Type = 0x102E, offset = 24, attrs = public]
              - LF_MEMBER [name = `MapOptions`, Type = 0x102E, offset = 40, attrs = public]
              - LF_MEMBER [name = `SessionName`, Type = 0x102E, offset = 56, attrs = public]
              - LF_MEMBER [name = `PlayDurationSeconds`, Type = 0x0074 (int), offset = 72, attrs = public]
              - LF_MEMBER [name = `SaveDateTime`, Type = 0x26F5, offset = 80, attrs = public]
              - LF_MEMBER [name = `SessionVisibility`, Type = 0xEDCD5, offset = 88, attrs = public]
              - LF_STMEMBER [name = `GUID`, type = 0x151D, attrs = public]
              - LF_ONEMETHOD [name = `~FSaveHeader`]
                type = 0xEDCD6, vftable offset = -1, attrs = public compiler-generated
              - LF_METHOD [name = `operator=`, # overloads = 2, overload list = 0xEDCDA]
              - LF_ONEMETHOD [name = `__vecDelDtor`]
                type = 0xEDCDB, vftable offset = -1, attrs = public compiler-generated
'''
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
        'wasPlacedInLevel': wasPlacedInLevel,
        'properties': []
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
        'outerPathName': outerPathName,
        'properties': []
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
        print('unknown type ' + str(type))
        assert False

print('type0Count: ' + str(type0Count))


elementCount = readInt()


def readNull():
    readHex(12)
    print(readLengthPrefixedString())
    readHex(4)


def readProperty():
    name = readLengthPrefixedString()
    if name == 'None':
        print('- [None]')
        return

    prop = readLengthPrefixedString()
  
    print('- ' + prop + ' ' + name)
    if prop == 'IntProperty':
        readHex(9)
        print(readInt())
    elif prop == 'StrProperty':
        readHex(9)
        print(readLengthPrefixedString())
        input()
    elif prop == 'StructProperty':
        readHex(8)
        type = readLengthPrefixedString()
        print('structType: ' + type)
        if type == 'Vector' or type == 'Rotator':
            readHex(29)  # TODO ...?
        elif type == 'Box':
            readHex(42)
        elif type == 'LinearColor':
            readHex(33)
        elif type == 'Transform':
            readHex(17)
            while (readProperty()):
                pass
        elif type == 'Quat':
            readHex(33)
        elif type == 'RemovedInstanceArray' or type == 'InventoryStack':
            readHex(17)  # TODO ...?
            while (readProperty()):
                pass
        elif type == 'InventoryItem':
            readHex(17)
            print(readLengthPrefixedString())
            print(readLengthPrefixedString())
            print(readLengthPrefixedString())
            print(readLengthPrefixedString())
            # while readProperty():
            #   pass
            readProperty()
            # can't consume null here because it might be needed by the overarching struct
            print('->>')
        else:
            print('Unknown type: ' + type)
            readHex(32)
            input()
            assert False

    elif prop == 'ArrayProperty':
        print(readInt())  # 964 length of the array property?
        print(readInt())  # 0
        itemType = readLengthPrefixedString()
        print('itemType: ' + itemType)
        readHex(1)
        count = readInt()
        print('count: ' + str(count))
        if itemType == 'ObjectProperty':
            for j in range(0, count):
                print(readLengthPrefixedString())
                print(readLengthPrefixedString())
        elif itemType == 'StructProperty':
            print(readLengthPrefixedString())
            print(readLengthPrefixedString())
            readHex(8)

            type = readLengthPrefixedString()  # MessageData
            print(type)

            readHex(17)
            # input()
            for i in range(0, count):
                while (readProperty()):
                    pass
            '''
            if type == 'MessageData':
                readHex(17)

                readProperty() # BooleanProperty WasRead
                readProperty() # ObjectProperty MessageClass
                print(readLengthPrefixedString()) # None
                readProperty()
                readProperty()
                print(readLengthPrefixedString()) # None
            else:
                readHex(17)
                readProperty() # StructProperty SpawnLocation
                readProperty() # ObjectProperty Creature
                readProperty() # BoolProperty WasKilled
                readProperty() # IntProperty KilledOnDayNr
                readProperty()
                readHex(32)
                input()
            '''
        elif itemType == 'IntProperty':
            for i in range(0, count):
                print(readInt())
        else:
            print('unknown itemType ' + itemType)
            readHex(32)
            input()
            assert False
    elif prop == 'ObjectProperty':
        readHex(9)
        print(readLengthPrefixedString())  # Persistent_Level
        print(readLengthPrefixedString())
    elif prop == 'BoolProperty':
        readHex(8)
        print(readByte())
        readHex(1)
        input()
    elif prop == 'FloatProperty':
        readHex(9)
        print(readFloat())
    elif prop == 'EnumProperty':
        print(readInt())  # 43
        readHex(4)
        print(readLengthPrefixedString())  # EIntroTutorialSteps
        readHex(1)
        # EIntroTutorialSteps::ITS_DISMANTLE_POD
        print(readLengthPrefixedString())
    elif prop == 'NameProperty':
        readHex(9)
        print(readLengthPrefixedString())
    elif prop == '':
        return False  # End of this Entity
    elif prop == 'MapProperty':
        readHex(8)
        print(readLengthPrefixedString())  # IntProperty
        print(readLengthPrefixedString())  # StructProperty
        readHex(5)

        count = readInt()
        print('count: ' + str(count))
        for i in range(0, count):
            readInt()
            readProperty()
            readProperty()

        '''
        print(readLengthPrefixedString()) # Buildables
        print(readLengthPrefixedString()) # ArrayProperty
        readHex(8)
        print(readLengthPrefixedString()) # ObjectProperty
        readHex(1)
        count = readInt()
        for i in range(0,count):
            print(readLengthPrefixedString()) # Persistent_Level
            print(readLengthPrefixedString()) # Persistent_Level:PersistentLevel.Build_Foundation_8x2_01_C_0
        '''

    elif prop == 'ByteProperty':
        readHex(8)
        unk1 = readLengthPrefixedString()  # EGamePhase
        print(unk1)
        if unk1 == 'EGamePhase':
            readHex(1)
            print(readLengthPrefixedString())  # EGP_MidGame
        elif unk1 == 'None':
            readHex(2)
        else:
            print('unknown byte property ' + unk1)
            readHex(32)
            readHex(32)
            readHex(32)
            input()

    elif prop == 'TextProperty':
        readHex(22)
        print(readLengthPrefixedString())

    else:
        print('Unknown property type: ' + prop)
        readHex(32)
        input()
        assert False

    return True

def readEntity(length):
    global bytesRead
    bytesRead = 0
    mapName = readLengthPrefixedString()
    entityName = readLengthPrefixedString()
    print('map: ' + mapName)
    print('entity: ' + entityName)

    childCount = readInt()  # TODO maybe child count? seems to
    if childCount > 0:
        print('children('+str(childCount)+'): [')
        for i in range(0, childCount):
            print('    ' + readLengthPrefixedString())
            print('    ' + readLengthPrefixedString())
        print(']')

    # print('..'+ str(bytesRead))
    while (readProperty()):
        print('------')
        pass
    missing = length - bytesRead
    if missing > 0:
        print('$ got missing ('+str(missing)+'):')
        readHex(missing)
        return
    if missing < 0:
        print('negative missing amount: ' + str(missing))
        readHex(32)
        input()
        assert False


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
    if i < 10203:
        readEntity(length)
    else:
        bytesRead = 0

        while readProperty():
            pass
        missing = length - bytesRead
        print('miss' + str(missing))
        if missing > 0:
            print('$ got missing ('+str(missing)+'):')
            readHex(missing)
        if missing < 0:
            print('negative missing amount: ' + str(missing))
            readHex(32)
            input()
            assert False
    # sys.stdout = sys.__stdout__

print('finished')

print(json.dumps(saveJson, indent=4))
input()
