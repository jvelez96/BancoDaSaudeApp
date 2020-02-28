import re
import random
import string

def validate_telemovel(n_telemovel):
    return True if len(str(n_telemovel)) == 9 and str(n_telemovel).startswith('9') else False

def validate_telefone(n_telefone):
    return True if len(str(n_telefone)) == 9 and str(n_telefone).startswith('2') else False


def validate_niss(niss):
    if not niss.isdigit() or len(niss) != 11:
        return False
    if niss[0] != '1' and niss[0] != '2':
        return False

    # control sum
    sum = int(niss[-1])
    prime_table = (29, 23, 19, 17, 13, 11, 7, 5, 3, 2)
    for i in range(0, 10):
        sum += int(niss[i]) * prime_table[i]
    return True if sum % 10 == 9 else False


# Control sum for BI and NIF
def validate_sum(num):
    control_sum = sum([int(dig) * (9 - i) for i, dig in enumerate(num[:-1])])
    remainder = control_sum % 11
    if num[-1] == '0' and (remainder == 0 or remainder == 1):
        return True
    elif int(num[-1]) == 11 - remainder:
        return True
    else:
        return False


def validate_nif(nif):
    nif = str(nif)
    if not len(nif) == 9 and nif[0] not in "125689":
        return False

    return validate_sum(nif)


def validate_bi(bi):
    if re.match(r'[0-9]{6,8}(\s*|-)[0-9]', bi):
        bi = bi.replace('-', '')

        for i in range(len(bi), 9):
            bi = '0' + bi

        return validate_sum(bi)
    else:
        return False


def validate_cc(cc):
    if re.match(r'[0-9]{8}(\s*|-)[0-9][a-zA-Z0-9]{3}', cc):
        cc = cc.replace('-', '').replace(' ', '')
        cc = list(cc)
        cc[9] = str(ord(cc[9].capitalize()) - 55) #Conversão de alfabeto
        cc[10] = str(ord(cc[10].capitalize()) - 55)
        cc = list(map(int, cc))

        sum = 0
        for i in range(0,len(cc)):
            if i%2 == 0:
                cc[i] *= 2
                if cc[i] >= 10:
                    cc[i] -= 9
            sum += cc[i]

        return sum % 10 == 0
    else:
        return False
