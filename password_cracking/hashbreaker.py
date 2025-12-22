import hashlib
from os import path
import os
import threading
import time
import sys
from pathlib import Path
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed

parser = argparse.ArgumentParser()
parser.add_argument("--wordlist", type=str,required=True)
parser.add_argument("--hash", type=str, required=True)

args = parser.parse_args()
wordlist_path = Path(args.wordlist)
obtained_hash = (args.hash)

if not wordlist_path.exists():
    print(f"Error: Wordlist '{args.wordlist}' not found!")
    print("Please check the path and try again.")
    sys.exit(1)

create_hash = lambda password: hashlib.sha256(password.encode('utf-8')).hexdigest()

def check_hash(chunk):
    for i in chunk:
        if obtained_hash == create_hash(i):
            return i #returns the password
    return None

def read_wordlist(wordlist_path):
    with open(wordlist_path, 'r', encoding = 'ISO-8859-1') as file:
        total_words = file.readlines()
        total_words = [line.strip() for line in total_words]
    return total_words

total_words = read_wordlist(wordlist_path)
    
def calculate_chunks(num_workers=None):
    if num_workers == None:
        num_workers = os.cpu_count()
    
    chunks_per_worker = 8
    chunk_size = len(total_words) // (num_workers * chunks_per_worker)
    min_chunk = 1000
    max_chunk = 100000
    return max(min_chunk, min(chunk_size, max_chunk))

def main():
    chunk_size = calculate_chunks()
    chunks = []
    for i in range (0, len(total_words), chunk_size):
        chunk = total_words[i:i+chunk_size]
        chunks.append(chunk)
    start = time.perf_counter()
    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(check_hash, chunk) for chunk in chunks]
        
        for future in as_completed(futures):
            result = future.result()
            if result != None:
                print(f"Password: {result}")
                end = time.perf_counter()
                elapsed = (end - start) * 1000
                print(f"Parallel Programming Method: Finished in {elapsed:.2f} miliseconds")
                raise SystemExit
    
if __name__ == '__main__':
    main()