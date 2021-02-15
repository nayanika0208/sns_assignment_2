import crccheck.crc
import numpy as np

FORMAT = "utf-8"
Key = np.array([ [-3, -3, -4],[0, 1, 1],[4, 3, 4]])
Key_inverse = np.array([[1, 0, 1],[4, 4, 3],[-4, -3, -3]])
Key_Dim=Key.shape[0]

encoding_dict={}
encoding_dict[' ']=27
for i in range(0,26):
    encoding_dict[chr(65+i)]=i+1


decoding_dict={}
decoding_dict[27]=' '
for i in range(1,27):
    decoding_dict[i]=chr(65+i-1)


def generateCRC(plain_txt):
    result = ''.join(format(i, 'b') for i in bytearray(plain_txt, encoding =FORMAT))
    return crccheck.crc.Crc32.calc(bytearray(result,encoding = FORMAT))