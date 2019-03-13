#!/usr/bin/env python3

import struct

import functools
import itertools
import csv
import binascii

def readcstr(f):
    toeof = iter(functools.partial(f.read, 1), '')
    return ''.join(itertools.takewhile(b'0'.__ne__, toeof))

f = open("test.sav", "rb")



levelWriter = csv.writer(open('levels.csv', 'w', newline=''))
objectWriter = csv.writer(open('objects.csv', 'w', newline=''))
objectTypeWriter = csv.writer(open('objectTypes.csv', 'w', newline=''))
elementWriter = csv.writer(open('elements.csv', 'w', newline=''))
pointWriter = csv.writer(open('points.csv', 'w', newline=''))
pointWriter.writerow(['x', 'y', 'z', 'type'])


bytesRead = 0


def readString(myfile):
    chars = []
    while True:
        c = myfile.read(1)
        #print(c)
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
    

def readHex(count):
    global bytesRead
    bytesRead += count

    chars = f.read(count)
    c = 0
    result = ''
    for i in chars:
        print(format(i, '02x'), end=' ')
        result += format(i, '02x') + ' '
        c+=1
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
        c+=1
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
print(readInt()) # Save Version
print(readInt()) # BuildVersion
print(readInt()) # SaveName (???)

print(readLengthPrefixedString()) # MapName
print(readLengthPrefixedString()) # MapOptions
print(readLengthPrefixedString()) # SessionName
print(readInt()) # PlayDurationSeconds
readHex(8) # SaveDateTime
# print(readLong())
readHex(1) # SessionVisibility

entryCount = readInt() #  total entries
print(entryCount)

print('///// END OF HEADER /////')

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


def readPersistentLevel():
    objectType = readObjectType()
    levelName = readLevelName()
    objectName = readObjectName()
    zero = readInt()
    if (zero != 0 and zero != 1):
        print(zero)
        input()

    a=readFloat()
    b=readFloat()
    c=readFloat()
    d=readFloat()
    x=readFloat()
    y=readFloat()
    z=readFloat()
    rest = readHex(16)

    if x == -2954079232.0 or z == 59927.625 or y == -1919341.0: # foliage removal
        return

    if (z > 50000):
        input()

    if x< -25000000:
        print(x)
        print(y)
        print(z)
        input()


    elementWriter.writerow([zero, rest, objectType, levelName, objectName, x, y, z, a, b, c, d])
    pointWriter.writerow([x,y,z,objectType])
    print('---')

def readPlayerState():
    readObjectType()
    readLevelName()
    readObjectName()
    print(readLengthPrefixedString())
    print('---')

def readPersistentLevelNone12():
    print(readInt())
    print(readString(f)) # None
    print(f.read(12))
    print(readString(f)) # Persistent_Level
    print(f.read(4))
    print(readString(f)) # Persistent_Level:PersistentLevel.FGWorldSettings
    print(f.read(4))
    print('---')

type0Count = 0

for i in range(0, entryCount):#10203):
    type = readInt()
    print('type: ' + str(type))
    if type == 1:
        readPersistentLevel()
    elif type == 0:
        readPlayerState()
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
    elif prop == 'StructProperty':
        readHex(8)
        type = readLengthPrefixedString()
        print('structType: ' + type)
        if type == 'Vector' or type == 'Rotator':
            readHex(29) # TODO ...?
        elif type == 'Box':
            readHex(42)
        elif type == 'RemovedInstanceArray' or type == 'InventoryStack':
            readHex(17) # TODO ...?
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
        print(readInt()) # 964 length of the array property?
        print(readInt()) # 0
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
            
            type = readLengthPrefixedString() #  MessageData
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
        elif  itemType == 'IntProperty':
            for i in range(0, count):
                print(readInt())
        else:
            print('unknown itemType ' + itemType)
            readHex(32)
            input()
            assert False
    elif prop == 'ObjectProperty':
        readHex(9)
        print(readLengthPrefixedString()) # Persistent_Level
        print(readLengthPrefixedString())
    elif prop == 'BoolProperty':
        readHex(10)
    elif prop == 'FloatProperty':
        readHex(9)
        print(readFloat())
    elif prop == 'EnumProperty':
        print(readInt()) # 43
        readHex(4)
        print(readLengthPrefixedString()) # EIntroTutorialSteps
        readHex(1)
        print(readLengthPrefixedString()) # EIntroTutorialSteps::ITS_DISMANTLE_POD
    elif prop == 'NameProperty':
        readHex(9)
        print(readLengthPrefixedString())
    elif prop == '':
        return False # End of this Entity
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
    print('entity: '+ entityName)

    childCount = readInt() # TODO maybe child count? seems to 
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
        


for i in range(0,elementCount):
    length = readInt()  # TODO: might actually be length of the following entry?
    print('length: ' + str(length))

#
        #print(readLengthPrefixedString())
        #print(readLengthPrefixedString())
        #readInt()
        #readProperty()
        #readProperty()
        #readProperty()
    print(': ' + str(i))
    if i < 10203:

        readEntity(length)
    else:
        bytesRead = 0

        while readProperty():
            pass
        missing = length - bytesRead
        print ('miss' + str(missing))
        if missing > 0:
            print('$ got missing ('+str(missing)+'):')
            readHex(missing)
        if missing < 0:
            print('negative missing amount: ' + str(missing))
            readHex(32)
            input()
            assert False
        
print('finished')