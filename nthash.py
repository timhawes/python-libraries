import binascii
import hashlib

def nthash(cleartext):
    return binascii.hexlify(hashlib.new('md4', cleartext.encode('utf-16le')).digest()).upper()
