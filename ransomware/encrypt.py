import argparse
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from getpass import getpass
import os
from pathlib import Path

parser = argparse.ArgumentParser(description="Encrypts files in a entire directory.")
parser.add_argument('--path', type = str, required = True)
args = parser.parse_args()
dir = Path(args.path)

#derive key from a password
def derive_key(password, salt: bytes = None):
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000
    )
    #runs the PBKDF2 algorithm on the password and encodes the 32 bytes into base64 url-safe string that fernet uses as a key
    #fernet expects key in base64 format
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key,salt

password = getpass("Enter your password: ")
key, salt = derive_key(password)
cipher = Fernet(key)

with open('salt.txt', 'wb') as f:
    f.write(salt)

def encrypt(file):
    with open(file, 'rb') as f:
        contents = f.read()
    contents_encrypted = cipher.encrypt(contents)
    
    with open(file,'wb') as f:
        f.write(contents_encrypted)

def main():
    for file in dir.rglob('*'):
        if file.name.endswith((".py,")) or file.name == (".env") or file.is_dir():
            continue
        encrypt(file)

if __name__ == "__main__":
    main()