import sys
from pathlib import Path
import os


# this functoin reads the input file and outputs an array without whitespaces
def readFile(arg):
    content = []
    if not os.path.exists(arg):
        sys.exit("File doesn't exist!")

    if Path(arg).suffix == '.asm':
        r = open(arg, "r")
        global line
        while True:
            line = r.readline()
            if not line: break
            content.append(line.strip())
        r.close()
    else:
        eof = Path(arg).suffix
        sys.stdout.write(f"Invalid file of type :{eof} \n")
        sys.exit('Only use files of type .asm')
    return content


# this function removes all the comments in the code
def removeComments(content):
    listOne = []
    subContent = []

    for index in range(len(content)):
        element = content[index]
        if (not element.startswith('//')):
            lol = element.strip()
            if (lol != ''):
                listOne.append(lol)
    for i in range(len(listOne)):
        curr = listOne[i].strip()

        commentindex = curr.split('//')
        subContent.append(commentindex[0])
    return subContent


# this function converts addresses into their corresponding 16bit binary values and outputs
def addressResolve(arr):
    arrOne = []
    address = {
        "R0": "0",
        "R1": "1",
        "R2": "2",
        "R3": "3",
        "R4": "4",
        "R5": "5",
        "R6": "6",
        "R7": "7",
        "R8": "8",
        "R9": "9",
        "R10": "10",
        "R11": "11",
        "R12": "12",
        "R13": "13",
        "R14": "14",
        "R15": "15",
        "SCREEN": "16384",
        "KBD": "24576",
        "SP": "0",
        "LCL": "1",
        "ARG": "2",
        "THIS": "3",
        "THAT": "4"
    }
    labelSymbols = {}
    count = 0
    variables = []
    vararr = []
    vardict = {}
    for i in range(len(arr)):
        ele = arr[i]

        if (ele.startswith('(') or ele.endswith(')')):  # stores the label values
            trueEle = ele[1:len(ele) - 1]  # remove parenthesis

            labelSymbols[trueEle] = i - count

            count += 1

        if not (ele.startswith('(') or ele.endswith(')')):  # removes the labels
            arrOne.append(ele)

    # now we will deal with the addresses
    # arrone contains the filtered array without the jump labels
    # in the next step we shall replace the jump labels with their corresponding values in label dict

    valueaddressList = list(labelSymbols.keys())
    addressList = list(address.keys())
    count = 0
    # collecting all the values with add symbols

    for i in range(len(arrOne)):
        element = arrOne[i]

        if element.startswith("@"):  # all addresses are selected
            # now we seperate the @ and the address

            splitlist = element.split('@')  # our address variable is in splitlist[1]
            pureAddress = splitlist[1].strip()

            if pureAddress.isdigit() or type(pureAddress) == int:
                binaryvalue = str(bin(int(pureAddress)).replace('0b', ''))
                if (len(binaryvalue) != 16):
                    diff = 16 - len(binaryvalue)
                    binaryvalue = "0" * diff + binaryvalue

                    element = binaryvalue

            if pureAddress in valueaddressList:  # only the jump addresses
                # now we replace the words with address values

                pureAddress = labelSymbols[pureAddress]  # replced with numbers
                binaryvalue = str(bin(int(pureAddress)).replace('0b', ''))
                if (len(binaryvalue) != 16):
                    diff = 16 - len(binaryvalue)
                    binaryvalue = "0" * diff + binaryvalue

                    element = binaryvalue

            if pureAddress in addressList:
                pureAddress = address[pureAddress]  # predefined addresses
                binaryvalue = str(bin(int(pureAddress)).replace('0b', ''))
                if (len(binaryvalue) != 16):
                    diff = 16 - len(binaryvalue)
                    binaryvalue = "0" * diff + binaryvalue

                    element = binaryvalue

            if not (pureAddress in addressList or pureAddress in valueaddressList or type(
                    pureAddress) == int or pureAddress.isdigit()):

                if pureAddress in vardict:
                    vardict[pureAddress] = vardict[pureAddress]
                else:
                    vardict[pureAddress] = 16 + count
                count += 1

                pureAddress = vardict[pureAddress]

                binaryvalue = str(bin(int(pureAddress)).replace('0b', ''))
                if (len(binaryvalue) != 16):
                    diff = 16 - len(binaryvalue)
                    binaryvalue = "0" * diff + binaryvalue

                    element = binaryvalue

        arrOne[i] = element

    return arrOne


# this function converts the remaining code into binary
def binaryHandler(arr):
    destination = {
        "null": 0b000,
        "M": 0b001,
        "D": 0b010,
        "MD": 0b011,
        "A": 0b100,
        "AM": 0b101,
        "AD": 0b110,
        "AMD": 0b111,
    }
    jump = {
        "null": 0b000,
        "JGT": 0b001,
        "JEQ": 0b010,
        "JGE": 0b011,
        "JLT": 0b100,
        "JNE": 0b101,
        "JLE": 0b110,
        "JMP": 0b111,
    }
    computation = {
        "0": 0b0101010,
        "1": 0b0111111,
        "-1": 0b0111010,
        "D": 0b0001100,
        "A": 0b0110000,
        "!D": 0b0001101,
        "!A": 0b0110001,
        "-D": 0b0001111,
        "-A": 0b0110011,
        "D+1": 0b0011111,
        "A+1": 0b0110111,
        "D-1": 0b0001110,
        "A-1": 0b0110010,
        "D+A": 0b0000010,
        "D-A": 0b0010011,
        "A-D": 0b0000111,
        "D&A": 0b0000000,
        "D|A": 0b0010101,
        "M": 0b1110000,
        "!M": 0b1110001,
        "-M": 0b1110011,
        "M+1": 0b1110111,
        "M-1": 0b1110010,
        "D+M": 0b1000010,
        "D-M": 0b1010011,
        "M-D": 0b1000111,
        "D&M": 0b1000000,
        "D|M": 0b1010101,

    }
    # the code is of the form destination=computation;jump
    # we need to output a binary code with the sequence 1 1 1 c1 c2 c3 c4 c5 c6 c7 d1 d2 d3 j1 j2 j3

    for i in range(len(arr)):
        element = arr[i]

        # select only C instructions

        if not (len(element) == 16):
            jmp = element.split(';')

            # jmp contains the split array those with two elements have predefined jump instruciton
            if (len(jmp) == 2):
                jmpcomp = jmp[0].strip()  # compbit
                jmpcomp = str(bin(computation[jmpcomp]).replace('0b', ''))
                if (len(jmpcomp) != 7):
                    diff = 7 - len(jmpcomp)
                    jmpcomp = "0" * diff + jmpcomp

                predefinedjmp = jmp[1].strip()
                predefinedjmp = str(
                    bin(jump[predefinedjmp]).replace('0b', ''))  # converts to binary based on lookup table
                if (len(predefinedjmp) != 3):
                    diff = 3 - len(predefinedjmp)
                    predefinedjmp = "0" * diff + predefinedjmp
                out = jmpcomp + "000" + predefinedjmp
                element = "111" + out

            elif (len(jmp) == 1):
                tmp = jmp[0].split("=")
                dest = tmp[0].strip()
                cmp = tmp[1].strip()

                dest = str(bin(destination[dest]).replace('0b', ''))
                if (len(dest) != 3):
                    diff = 3 - len(dest)
                    dest = "0" * diff + dest

                cmp = str(bin(computation[cmp]).replace('0b', ''))
                if (len(dest) != 7):
                    diff = 7 - len(cmp)
                    cmp = "0" * diff + cmp

                jmp = cmp + dest + "000"
                element = "111" + jmp

        arr[i] = element

    return arr


def writeFile(arg, arr):
    filename = Path(arg).stem
    os.chdir('../')
    cwd=os.getcwd()

    os.makedirs(f"{cwd}/Output",exist_ok=True)

    fullPath=f"Output/{filename}"

    with open(f"{fullPath}.hack", 'w') as f:
        for ele in arr:
            f.write(f"{ele}\n")
    f.close()


if len(sys.argv) != 2:
    sys.exit('Must provide a file')
else:
    fileOutput = readFile(sys.argv[1])
    commentRemoved = removeComments(fileOutput)
    addressResolved = addressResolve(commentRemoved)
    binout = binaryHandler(addressResolved)
    writeFile(sys.argv[1], binout)
