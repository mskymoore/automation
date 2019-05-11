import fileinput, sys, re, os

modeRegex = re.compile(r'\s*mode:\s\d{3,4}')

permissionsDict = { '1': 'x',
                    '2': 'w',
                    '3': 'wx',
                    '4': 'r',
                    '5': 'rx',
                    '6': 'rw',
                    '7': 'rwx'}


def convertMode(mode):

    modeLen = len(mode)

    if modeLen == 4:
        specialDigit = mode[0]
        userDigit = mode[1]
        groupDigit = mode[2]
        otherDigit = mode[3]
    elif modeLen == 3:
        specialDigit = '0'
        userDigit = mode[0]
        groupDigit = mode[1]
        otherDigit = mode[2]
    else:
        raise NotImplementedError(f'Mode string {mode} length is not 3 or 4')

    userString = 'u='
    groupString = 'g='
    otherString = 'o='

    if userDigit != '0':
        userString += permissionsDict[userDigit]
    if groupDigit != '0':
        groupString += permissionsDict[groupDigit]
    if otherDigit != '0':
        otherString += permissionsDict[otherDigit]

    specialBits = format(int(specialDigit), '3b')

    if specialBits[0] == '1':
        userString += 's'
    if specialBits[1] == '1':
        groupString += 's'
    if specialBits[2] == '1':
        otherString += 't'

    uncheckedPermissionsStrings = [userString, groupString, otherString]
    permissionsStrings = []

    for s in uncheckedPermissionsStrings:
        if len(s) > 2:
            permissionsStrings.append(s)

    permissionsString = ','.join(permissionsStrings)

    return permissionsString


def replaceAll(the_file):

    with fileinput.input(the_file, inplace=1, backup='.old') as the_file:
        for line in the_file:
            match = modeRegex.match(line)
            if match is not None:
                mode = match.group(0).split()[1]
                line = line.replace(mode, f"'{convertMode(mode)}'")
            sys.stdout.write(line)


def main():

    for root, subfolders, files in os.walk(sys.argv[1]):
        for aFile in files:
            if '.yml' in aFile:
                print(f"Replacing occurences in {root + aFile}\n")
                replaceAll(root + aFile)

if __name__ == '__main__':
    main()
