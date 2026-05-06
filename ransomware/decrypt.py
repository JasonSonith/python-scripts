import argparse
import base64
from concurrent.futures import ThreadPoolExecutor
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import getpass
import os
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--path', type = str, required = False)
args = parser.parse_args()

if args.path:
    dir = Path(args.path)
else:
    dir = Path('test')

def derive_key(password, salt: bytes = None):
    
    kdf = PBKDF2HMAC (
        algorithm = hashes.SHA256(),
        length = 32,
        salt = salt,
        iterations = 100000
    )
    
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt

password = getpass.getpass('Enter the password to decrypt the files: ')

with open(dir.parent / 'salt.txt', 'rb') as f:
    salt = f.read()

key, salt = derive_key(password, salt)
cipher = Fernet(key)

def decrypt(file):
    
    print(f"Decrypting {file}...")
    
    with open(file, 'rb') as f:
        contents = f.read()
    contents_decrypted = cipher.decrypt(contents)
    
    with open(file, 'wb') as f:
        f.write(contents_decrypted)
    
    print(f"Finished decrypting {file}!")

def main():
    with ThreadPoolExecutor(max_workers= os.cpu_count()) as executor:
        executor.map(decrypt, dir.rglob('*'))

if __name__ == '__main__':
    main()