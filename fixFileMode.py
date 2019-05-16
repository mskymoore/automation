import fileinput, sys, re, os, logging
from argparse import ArgumentParser
from pathlib import Path



parser = ArgumentParser()
parser.add_argument('-p', '--path', help='The path to the directory to search for .yml files and make changes.',
                    type=str, metavar='/path/to/some/dir/', required=True)
args = parser.parse_args()

# regular expressions to search for in files
regexs = [re.compile(r'\s*mode:\s\d{3,4}'),
          re.compile(r'\s*mode:\s\"\d{3,4}\"'),
          re.compile(r'\s*mode:\s\'\d{3,4}\'')]

# map octal digits to symbolic permissions
permissionsDict = { '1': 'x',
                    '2': 'w',
                    '3': 'wx',
                    '4': 'r',
                    '5': 'rx',
                    '6': 'rw',
                    '7': 'rwx'}

log = logging.getLogger()

# takes a numeric mode in the forms 7777, '7777', or "7777"
# returns a symbolic version: 'u=rwxs,g=rwxs,o=rwxt'
def convertMode(mode):

    checkMode = mode.strip('"\'')
    for digit in checkMode:
        if int(digit) > 7:
            log.warning(f'A mode digit cannot be greater than 7, {mode} was passed as a mode.\
                          \nTHIS WILL BE LEFT AS IS: {mode}')
            return mode

    mode = checkMode
    modeLen = len(mode)

    # these should always be 3 or 4 digits
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

    # user, group, and other permission seed strings
    userString = 'u='
    groupString = 'g='
    otherString = 'o='

    # if the digit is 0, do nothing, otherwise
    # look up the symbolic permission in the dictionary
    if userDigit != '0':
        userString += permissionsDict[userDigit]
    if groupDigit != '0':
        groupString += permissionsDict[groupDigit]
    if otherDigit != '0':
        otherString += permissionsDict[otherDigit]

    # convert the special digit to 3 binary digits
    # assuming it's not larger than 7 which would be
    # an invalid value
    specialBits = format(int(specialDigit), '3b')

    if specialBits[0] == '1':
        userString += 's'
    if specialBits[1] == '1':
        groupString += 's'
    if specialBits[2] == '1':
        otherString += 't'

    uncheckedPermissionsStrings = [userString, groupString, otherString]
    permissionsStrings = []

    # if the strings are only 2 characters long,
    # there were no permissions mentioned for that type
    for s in uncheckedPermissionsStrings:
        if len(s) > 2:
            permissionsStrings.append(s)

    # join the permissionsStrings with ',' characters between them
    permissionsString = '"' + ','.join(permissionsStrings) + '"'

    return permissionsString


def replaceAll(the_file):

    global regexs
    # read the file and search for matches to regexs
    with open(the_file, mode='r') as the_file_object:
        the_file_contents = the_file_object.read()

        for regex in regexs:
            result = regex.search(the_file_contents)
            if result is not None:
                print(f'Replacing occurences in {the_file}.')
                break

        if result is None:
            print(f'No occurences in {the_file}.')
            return


    # rewrite the_file in place, renaming the original to the_file.old
    with fileinput.input(the_file, inplace=1, backup='.old') as the_file:
        for line in the_file:
            for regex in regexs:
                match = regex.match(line)
                if match is not None:
                    mode = match.group(0).split()[1]
                    line = line.replace(mode, f"{convertMode(mode)}")
                    continue
            sys.stdout.write(line)


def main():

    global args
    aDirectory = Path(args.path).resolve()
    if not aDirectory.exists():
        raise FileNotFoundError(f'{aDirectory} does not exist or could not be accessed.')
    elif not aDirectory.is_dir():
        raise NotADirectoryError(f'{aDirectory} is not a directory.')
    else:
        print(f'\nRecursively searching {str(aDirectory) + "/"} for .yml files...\n')
        # recursively walk through directory passed to this file
        for root, subfolders, files in os.walk(aDirectory):
            # for each file in all subdirectories
            for aFile in files:
                # if the file name ends in .yml
                if '.yml' == aFile[-4:]:
                    print(f"\nSearching for occurences in {root + '/' + aFile}...")
                    replaceAll(root + '/' + aFile)


if __name__ == '__main__':
    main()
