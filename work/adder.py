from math import *

N = 8
V = 4
Z = 2
C = 1

wordSign = 1 << 11
wordMask = (1 << 12) - 1
byteSign = 1 << 7
byteMask = (1 << 8) - 1

def adder(op, a, b, cin, siz=False):
    if siz:
        sign = wordSign
        mask = wordMask
    else:
        sign = byteSign
        mask = byteMask

    auL = mask & a
    if op == 1:
        auR = mask & ~b
    else:
        auR = mask & b
    din = mask & b

    sum = auL + auR + cin

    nvzc = 0
    if sign & sum:
        nvzc |= N
    if (~(auL ^ auR) & (auL ^ sum)) & sign:
        nvzc |= V
    if (mask & sum) == 0:
        nvzc |= Z
    if sum > mask:
        nvzc |= C
        sum &= mask

    return nvzc, sum, auL, auR

print(N, V, Z, C, '%04X %04X %02X %02X' % (wordSign, wordMask, \
                                           byteSign, byteMask))
stat ={0 :'----',
       1 :'---C',
       2 :'--Z-',
       3 :'--ZC',
       4 :'-V--',
       5 :'-V-C',
       6 :'-VZ-',
       7 :'-VZC',
       8 :'N---',
       9 :'N--C',
       10:'N-Z-',
       11:'N-ZC',
       12:'NV--',
       13:'NV-C',
       14:'NVZ-',
       15:'NVZC' }
        
with open("adder08b.txt", "wt") as fout:
    k = 0
    for i in range(256):
        for j in range(256):
            nvzc, sum, auL, auR = adder(0, i, j, 0)
            print('%s, %1d, %02X, %02X, %02X, %02X, %02X, %1d' % \
                  (stat[nvzc], 0, sum, i, j, auL, auR, 0), file=fout)
            nvzc, sum, auL, auR = adder(0, i, j, 1)
            print('%s, %1d, %02X, %02X, %02X, %02X, %02X, %1d' % \
                  (stat[nvzc], 0, sum, i, j, auL, auR, 1), file=fout)
            nvzc, sum, auL, auR = adder(1, i, j, 1)
            print('%s, %1d, %02X, %02X, %02X, %02X, %02X, %1d' % \
                  (stat[nvzc], 1, sum, i, j, auL, auR, 1), file=fout)
            nvzc, sum, auL, auR = adder(1, i, j, 0)
            print('%s, %1d, %02X, %02X, %02X, %02X, %02X, %1d' % \
                  (stat[nvzc], 1, sum, i, j, auL, auR, 0), file=fout)
        if k == 0:
            print('%02X' % (i), end='')
        else:
            print(', %02X' % (i), end='')
        k += 1
        if k == 16:
            print()
            k = 0
