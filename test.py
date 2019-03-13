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
    assert zero == b'\x00'
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

input()
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
        print(readLengthPrefixedString()) #  Vector
        readHex(29) # TODO ...?
    elif prop == 'ArrayProperty':
        print(readInt()) # 964 length of the array property?
        print(readInt()) # 0
        itemType = readLengthPrefixedString()
        print('itemType: ' + itemType)

        if itemType == 'ObjectProperty':
            readHex(1)
            count = readInt()
            print('count: ' + str(count))
            for j in range(0, count):
                print(readLengthPrefixedString())
                print(readLengthPrefixedString())
        elif itemType == 'StructProperty':
            readHex(1)
            count = readInt()
            print('count: ' + str(count))
            print(readLengthPrefixedString())
            print(readLengthPrefixedString())
            readHex(8)
            print(readLengthPrefixedString()) #  MessageData
            readHex(17)

            readProperty() # BooleanProperty WasRead
            readProperty() # ObjectProperty MessageClass
            print(readLengthPrefixedString()) # None
            readProperty()
            readProperty()
            print(readLengthPrefixedString()) # None

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

    print('children: [')
    for i in range(0, childCount):
        print('    ' + readLengthPrefixedString())
        print('    ' + readLengthPrefixedString())
    print(']')
    
    # print('..'+ str(bytesRead))
    while (readProperty()):
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
        


for i in range(0,500):
    type = readInt()  # TODO: might actually be length of the following entry?
    print('type: ' + str(type))
    if type == 25:
        readEntity(type)
    elif type == 91:
        readEntity(type)
    elif type == 96:
        readEntity(type)
    elif type == 92:
        readEntity(type)

    elif type == 1286:
        readEntity(type)
        '''
        print(readLengthPrefixedString()) # Persistent_Level
        print(readLengthPrefixedString()) # Persistent_Level:PersistentLevel.BP_GameState_C_0
        print(readInt()) # 0
        print(readLengthPrefixedString()) # mAvailableRecipes
        print(readLengthPrefixedString()) # ArrayProperty
        print(readInt()) # 1126 length of the array property?
        print(readInt()) # 0
        print(readLengthPrefixedString()) # ObjectProperty
        readHex(1)
        count = readInt()
        print(count)
        for j in range(0, count):
            readHex(4)
            print(readLengthPrefixedString()) # /Game/FactoryGame/Recipes/Smelter/Recipe_IngotIron.Recipe_IngotIron_C
        
        print(readLengthPrefixedString()) # None
        print(readInt()) # 0
        '''
    elif type == 2640:
        readEntity(type)
        '''
        print(readLengthPrefixedString()) # Persistent_Level
        print(readLengthPrefixedString()) # Persistent_Level:PersistentLevel.BP_GameState_C_0
        print(readInt()) # 0
        print(readLengthPrefixedString()) # mAvailableSchematics
        print(readLengthPrefixedString()) # ArrayProperty
        print(readInt()) # 2419 length of the array property?
        print(readInt()) # 0
        print(readLengthPrefixedString()) # ObjectProperty
        readHex(1)
        count = readInt()
        print(count)
        for j in range(0, count):
            readHex(4)
            print(readLengthPrefixedString()) # /Game/FactoryGame/Recipes/Smelter/Recipe_IngotIron.Recipe_IngotIron_C

        print(readLengthPrefixedString()) # mShipLandTimeStampSave
        print(readLengthPrefixedString()) # FloatProperty
        readHex(9)
        print(readInt())
        print(readLengthPrefixedString()) # None
        print(readLengthPrefixedString()) # [empty]
        '''
    elif type == 192:
        readEntity(type)
        '''
        print(readLengthPrefixedString()) # Persistent_Level
        print(readLengthPrefixedString()) # Persistent_Level:PersistentLevel.BP_GameState_C_0
        print(readInt()) # 0
        print(readLengthPrefixedString()) # mDaySeconds
        print(readLengthPrefixedString()) # FloatProperty
        readHex(9)
        print(readInt())
        print(readLengthPrefixedString()) # mNumberOfPassedDays
        print(readLengthPrefixedString()) # IntProperty
        readHex(9)
        print(readInt())
        print(readLengthPrefixedString()) # None
        print(readLengthPrefixedString()) # [empty]
        '''
    elif type == 264:
        readEntity(type)
        '''
        print(readLengthPrefixedString()) # Persistent_Level
        print(readLengthPrefixedString()) # Persistent_Level:PersistentLevel.BP_GameState_C_0
        print(readInt()) # 0
        print(readLengthPrefixedString()) # mPendingTutorial
        print(readLengthPrefixedString()) # EnumProperty
        print(readInt()) # 43
        readHex(4)
        print(readLengthPrefixedString()) # EIntroTutorialSteps
        readHex(1)
        print(readLengthPrefixedString()) # EIntroTutorialSteps::ITS_DISMANTLE_POD
        print(readLengthPrefixedString()) # mHasCompletedIntroSequence
        print(readLengthPrefixedString()) # BoolProperty
        readHex(10)
        print(readLengthPrefixedString()) # None
        print(readLengthPrefixedString()) # [empty]
        '''
    elif type == 154:
        readEntity(type)
        '''
        print(readLengthPrefixedString()) # [empty]
        print(readLengthPrefixedString()) # [empty]
        print(readInt()) # 0
        print(readLengthPrefixedString()) # mPendingTutorial
        print(readLengthPrefixedString()) # StrProperty
        readHex(9)
        print(readLengthPrefixedString()) # empty
        print(readLengthPrefixedString()) # mStartingPointTagName
        print(readLengthPrefixedString()) # NameProperty
        readHex(9)
        print(readLengthPrefixedString()) # Grass Fields
        print(readLengthPrefixedString()) # None
        print(readLengthPrefixedString()) # [empty]
        readHex(4)
        '''
    elif type == 2006:
        readEntity(type)
        '''
        print(readLengthPrefixedString()) # [empty]
        print(readLengthPrefixedString()) # [empty]
        print(readInt()) # 0
        print(readLengthPrefixedString()) # mTimeSubsystem
        print(readLengthPrefixedString()) # ObjectProperty
        readHex(9)
        print(readLengthPrefixedString()) # Persistent_Level
        print(readLengthPrefixedString()) # Persistent_Level:PersistentLevel.TimeSubsystem
        print(readLengthPrefixedString()) # mStorySubsystem
        print(readLengthPrefixedString()) # ObjectProperty
        readHex(9)
        print(readLengthPrefixedString()) # Persistent_Level
        print(readLengthPrefixedString()) # Persistent_Level:PersistentLevel.StorySubsystem
        print(readLengthPrefixedString()) # mRailroadSubsystem
        print(readLengthPrefixedString()) # ObjectProperty
        readHex(9)
        print(readLengthPrefixedString()) # Persistent_Level
        print(readLengthPrefixedString()) # Persistent_Level:PersistentLevel.RailroadSubsystem
        print(readLengthPrefixedString()) # mCircuitSubsystem
        print(readLengthPrefixedString()) # ObjectProperty 
        readHex(9)
        print(readLengthPrefixedString()) # Persistent_Level
        print(readLengthPrefixedString()) # Persistent_Level:PersistentLevel.CircuitSubsystem
        print(readLengthPrefixedString()) # mRecipeManager
        print(readLengthPrefixedString()) # ObjectProperty 
        readHex(9)
        print(readLengthPrefixedString()) # Persistent_Level
        print(readLengthPrefixedString()) # Persistent_Level:PersistentLevel.recipeManager
        print(readLengthPrefixedString()) # mSchematicManager
        print(readLengthPrefixedString()) # ObjectProperty 
        readHex(9)
        print(readLengthPrefixedString()) # Persistent_Level
        print(readLengthPrefixedString()) # Persistent_Level:PersistentLevel.schematicManager
        print(readLengthPrefixedString()) # mGamePhaseManager
        print(readLengthPrefixedString()) # ObjectProperty 
        readHex(9)
        print(readLengthPrefixedString()) # Persistent_Level
        print(readLengthPrefixedString()) # Persistent_Level:PersistentLevel.GamePhaseManager
        print(readLengthPrefixedString()) # mResearchManager
        print(readLengthPrefixedString()) # ObjectProperty 
        readHex(9)
        print(readLengthPrefixedString()) # Persistent_Level
        print(readLengthPrefixedString()) # Persistent_Level:PersistentLevel.ResearchManager
        print(readLengthPrefixedString()) # mTutorialIntroManager
        print(readLengthPrefixedString()) # ObjectProperty 
        readHex(9)
        print(readLengthPrefixedString()) # Persistent_Level
        print(readLengthPrefixedString()) # Persistent_Level:PersistentLevel.TutorialIntroManager
        print(readLengthPrefixedString()) # mActorRepresentationManager
        print(readLengthPrefixedString()) # ObjectProperty 
        readHex(9)
        print(readLengthPrefixedString()) # Persistent_Level
        print(readLengthPrefixedString()) # Persistent_Level:PersistentLevel.ActorRepresentationManager
        print(readLengthPrefixedString()) # mScannableResources
        print(readLengthPrefixedString()) # ArrayProperty 
        print(readInt()) # 88 length of the array property?
        print(readInt()) # 0
        print(readLengthPrefixedString()) # ObjectProperty
        readHex(1)
        count = readInt()
        print(count)
        for j in range(0, count):
            readHex(4)
            print(readLengthPrefixedString())

        print(readLengthPrefixedString()) # mVisitedMapAreas
        print(readLengthPrefixedString()) # ArrayProperty 
        print(readInt()) # 113 length of the array property?
        print(readInt()) # 0
        print(readLengthPrefixedString()) # ObjectProperty
        readHex(1)
        count = readInt()
        print(count)
        for j in range(0, count):
            readHex(4)
            print(readLengthPrefixedString())




        readProperty() # mPlayDurationWhenLoaded
        readProperty() # mReplicatedSessionName
        readProperty() # mFirstPawnLocation
        readProperty() # mFirstPawnRotation
        
        readProperty() # None
        # readHex(4)
        #print(readLengthPrefixedString()) 
        #print(readLengthPrefixedString()) # [empty]
        '''
    elif type == 2222:
        readEntity(type)
    elif type == 285:
        readEntity(type)
    elif type == 1089 \
        or type == 396 \
        or type == 397 \
        or type == 379 \
        or type == 377 \
        or type == 381 \
        or type == 376:
        readEntity(type)
    elif type == 1:
        print(readLengthPrefixedString()) # Persistent_Level
        print(readLengthPrefixedString()) # Persistent_Level:PersistentLevel.BP_PlayerState_C_0
        print(readInt()) # 0
        print(readLengthPrefixedString()) # [empty]
        print(readLengthPrefixedString()) # [empty]
        readHex(4)
        readProperty() # mHotbarShortcuts
        readProperty() # mOwnedPawn
        readProperty() # mHasReceivedInitialItems
        readProperty() # mHasSetupDefaultShortcuts
        readProperty() # mTutorialSubsystem
        readProperty() # mMessageData
        readProperty() # mRememberedFirstTimeEquipmentClasses
        readProperty() # None

        readHex(34) # TODO ?????
        readProperty() # mBuildableSubsystem
        readProperty() # mFoundationSubsystem
        readProperty() # None


        readHex(32)
        input()
    else:
        print('unknown type ' + str(type))

        readHex(32)
        input()
        assert False

    if type != 25:
        print('>>>>>> bytesRead: ' + str(bytesRead) + '/' + str(type))
        # input()
readHex(32)
input()

#for i in range(0,577): # range(0, 577):
    #readPlayerState()
    #print(i)
#
#input()

readPersistentLevelNone12()

readPersistentLevelNone12()

print(readInt())
print(readString(f)) # None
print(f.read(16))
print(readString(f)) # Persistent_Level
print(f.read(4))
print(readString(f)) # Persistent_Level:PersistentLevel.FGWorldSettings
print(f.read(4))
print('---')

readPersistentLevelNone12()
readPersistentLevelNone12()

print(readInt())
print(readString(f)) # None
print(f.read(16))
print(readString(f)) # Persistent_Level
nprint(f.read(4))
print(readString(f)) # Persistent_Level:PersistentLevel.BP_GameState_C_0
nprint(f.read(8))
print(readString(f)) # mAvailableRecipes
nprint(f.read(4))
print(readString(f)) # ArrayProperty
print(f.read(12))
print(readString(f)) # ObjectProperty
print(f.read(1))
object_count = int.from_bytes(f.read(1), byteorder='big')
print(f.read(3))

def readRecipe():
    print(f.read(8))
    print(readString(f)) # /Game/FactoryGame/Recipes/Smelter/Recipe_IngotIron.Recipe_IngotIron_C
    

for i in range(0, object_count):
    readRecipe()
    print(i)


print('###')
readPersistentLevelNone12()

print(f.read(4))
## TODO merge with function above
print(readString(f)) # None
print(readLevelName())
print(f.read(12))
print(readString(f)) # Persistent_Level
nprint(f.read(4))
print(readString(f)) # Persistent_Level:PersistentLevel.BP_GameState_C_0
nprint(f.read(8))

print(readString(f)) # mAvailableSchematics
nprint(f.read(4))
print(readString(f)) # ArrayProperty
print(f.read(12))
print(readString(f)) # ObjectProperty
print(f.read(1))
object_count = int.from_bytes(f.read(1), byteorder='big')
print(f.read(3))

for i in range(0,object_count):
    readRecipe()



print(f.read(4))
print(readString(f)) # mShipLandTimeStampSave
print(f.read(4))
print(readString(f)) # FloatProperty
print(f.read(17))
print(readString(f)) # None
print(f.read(12))
print(readString(f)) # Persistent_Level
print(f.read(4))
print(readString(f)) # Persistent_Level:PersistentLevel.BP_GameState_C_0
print(f.read(8))

print(readString(f)) # None
print(f.read(12))
print(readString(f)) # Persistent_Level
print(f.read(4))
print(readString(f)) # Persistent_Level:PersistentLevel.BP_GameState_C_0

print(f.read(8))
print(readString(f)) # mDaySeconds
print(f.read(4))
print(readString(f)) # FloatProperty
print(f.read(17))
print(readString(f)) # mNumberOfPassedDays
print(f.read(4))
print(readString(f)) # IntProperty
print(f.read(17))
print(readString(f)) # None
print(f.read(12))
print(readString(f)) # Persistent_Level
print(f.read(4))
print(readString(f)) # Persistent_Level:PersistentLevel.BP_GameState_C_0

print(f.read(8))
print(readString(f)) # mPendingTutorial
print(f.read(4))
print(readString(f)) # EnumProperty
print(f.read(12))
print(readString(f)) # EIntroTutorialSteps
print(f.read(5))
print(readString(f)) # EIntroTutorialSteps::ITS_DISMANTLE_POD
print(f.read(4))
print(readString(f)) # mHasCompletedIntroSequence
print(f.read(4))
print(readString(f)) # BoolProperty
print(f.read(14))

print(readString(f)) # None
print(f.read(24))
print(readString(f)) # mSaveSessionName
print(f.read(4))
print(readString(f)) # StrProperty
print(f.read(13))
print(readString(f)) # empty
print(f.read(4))
print(readString(f)) # mStartingPointTagName
print(f.read(4))
print(readString(f)) # NameProperty
print(f.read(13))
print(readString(f)) # Grass Fields
print(f.read(4))
print(readString(f)) # None
print(f.read(28))

def readSubsystem():
    print(readString(f)) # mTimeSubsystem
    print(f.read(4))
    print(readString(f)) # ObjectProperty
    print(f.read(9))
    readLevelName()
    readObjectName()
    print(f.read(4))
    print('---')

for i in range(0, 10):
    readSubsystem()

print(readString(f)) # mTimeSubsystem
print(f.read(4))
print(readString(f)) # ArrayProperty
print(f.read(12))
print(readString(f)) # ObjectProperty
print(f.read(13))
print(readString(f)) # /Game/FactoryGame/Resource/RawResources/OreIron/Desc_OreIron.Desc_OreIron_C
print(f.read(4))

print(readString(f)) # mVisitedMapAreas
print(f.read(4))
print(readString(f)) # ArrayProperty
print(f.read(12))
print(readString(f)) # ObjectProperty
print(f.read(13))
print(readString(f)) # /Game/FactoryGame/Interface/UI/Minimap/MapAreaPersistenLevel/Area_GrassFields_3.Area_GrassFields_3_C
print(f.read(4))

print(readString(f)) # mPlayDurationWhenLoaded
print(f.read(4))
print(readString(f)) # IntProperty
print(f.read(17))

print(readString(f)) # mReplicatedSessionName
print(f.read(4))
print(readString(f)) # StrProperty
print(f.read(13))
print(readString(f)) # empty
print(f.read(5))

print(readString(f)) # FirstPawnLocation
print(f.read(4))
print(readString(f)) # StructProperty
print(f.read(12))
print(readString(f)) # Vector
print(f.read(33))

print(readString(f)) # FirstPawnLocation
print(f.read(4))
print(readString(f)) # StructProperty
print(f.read(12))
print(readString(f)) # Rotator
print(f.read(33))

print(readString(f)) # None
print(f.read(12))
print(readString(f)) # Persistent_Level
print(f.read(4))
print(readString(f)) # Persistent_Level:PersistentLevel.BP_PlayerState_C_0
print(f.read(16))

print('>>>')
print(f.read(4))
print(readString(f)) # mHotbarShortcuts
print(f.read(4))
print(readString(f)) # ArrayProperty
print(f.read(12))
print(readString(f)) # ObjectProperty
print(f.read(5))

def readShortcut():
    readLevelName()
    readObjectName()
    
    print("--")

for i in range(0,10):
    readShortcut()


print(readInt())
print(readString(f)) # mOwnedPawn
print(readInt())
print(readString(f)) # ObjectProperty
print(f.read(9))
readLevelName()
readObjectName()

print(readInt())
print(readString(f)) # mOwnedPawn
print(readInt())
print(readString(f)) # BoolProperty
print(f.read(10))

print(readInt())
print(readString(f)) # mHasSetupDefaultShortcuts
print(readInt())
print(readString(f)) # BoolProperty
print(f.read(10))

print(readInt())
print(readString(f)) # mTutorialSubsystem
print(readInt())
print(readString(f)) # ObjectProperty
print(f.read(9))
readLevelName()
readObjectName()

print('-----')
print(readInt())
print(readString(f)) # mMessageData
print(readInt())
print(readString(f)) # ArrayProperty
print(f.read(12))
print(readString(f)) # StructProperty
print(f.read(9))
print(readString(f)) # mMessageData
print(readInt())
print(readString(f)) # StructProperty
print(f.read(12))
print(readString(f)) # mMessageData
print(f.read(17))

def readMessage():
    print(readInt())
    print(readString(f)) # WasRead
    print(readInt())
    print(readString(f)) # BoolProperty
    print(f.read(10))
    print(readInt())
    print(readString(f)) # MessageClass
    print(readInt())
    print(readString(f)) # ObjectProperty
    print(f.read(17))
    print(readString(f)) # /Game/FactoryGame/Interface/UI/Message/Tutorial/IntroTutorial/IntroTutorial_Greeting.IntroTutorial_Greeting_C
    print(readInt())
    print(readString(f)) # None

for i in range(0,2):
    readMessage()


print('-----')
print(readInt())
print(readString(f)) # mMessageData
print(readInt())
print(readString(f)) # ArrayProperty
print(f.read(12))
print(readString(f)) # ObjectProperty
print(f.read(13))
print(readString(f)) # /Game/FactoryGame/Equipment/ResourceScanner/BP_ResourceScanner.BP_ResourceScanner_C
print(readInt())
print(readString(f)) # None
print(f.read(38))

print('')
print('........')
print(f.read(32))
print('')