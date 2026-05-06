import argparse
import time
from pathlib import Path
import hashlib

parser = argparse.ArgumentParser()
parser.add_argument('--wordlist', type=str, required = True)
parser.add_argument('--hash', type=str, required = True)
args = parser.parse_args()
wordlist = Path(args.wordlist)
obtained_hash = args.hash

def read_wordlist(wordlist_path):
    with open(wordlist_path, 'r', encoding = 'ISO-8859-1') as file:
        total_words = file.readlines()
        total_words = [line.strip() for line in total_words]
    return total_words

total_words = read_wordlist(wordlist)

start = time.perf_counter()
for password in total_words:
    hash = hashlib.sha256(b'password').hexdigest()
    if obtained_hash == hash:
        print(f"Password is {password}")
        break

end = time.perf_counter()
elapsed = (end - start) * 1000
print(f"Brute Force Method: Finished in {elapsed:.2f} miliseconds")
