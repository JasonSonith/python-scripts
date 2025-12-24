
# Python Automation Scripts

A collection of Python scripts I've built to practice automation, concurrency, and general problem-solving. Each project is self-contained with its own documentation.

## Projects

### Password Hash Cracker

A concurrent hash cracker using Python's `ProcessPoolExecutor` to distribute work across CPU cores. Built to learn about parallel processing and CPU-bound tasks.

**Features:**
- Multi-process execution with automatic chunk sizing
- Early termination when password is found
- Handles large wordlists (tested with rockyou.txt)
- Includes single-threaded version for performance comparison

**Usage:**
```bash
python password_cracking/hashbreaker.py --wordlist wordlists/rockyou.txt --hash <sha256_hash>
```

**For educational purposes only.** Don't use this on systems you don't own.

### File Encryptor/Decryptor

A simple encryption tool that locks down all files in a directory using Fernet encryption. Uses PBKDF2 to turn your password into a secure key. Built this to learn how symmetric encryption works in practice.

**Features:**
- Password-based encryption (no need to manage key files)
- Recursively encrypts all files in subdirectories
- Uses `ThreadPoolExecutor` for faster encryption on large directories
- Skips `.py` and `.env` files so you don't accidentally lock yourself out

**Usage:**
```bash
# Encrypt a directory
python ransomware/encrypt.py --path /path/to/folder

# Decrypt it back
python ransomware/decrypt.py --path /path/to/folder
```

**For educational purposes only.** Seriously, don't be that person.

### More Coming

Planning to add scripts for web scraping, API automation, and network tools as I build them out.

## Setup

```bash
git clone <repository-url>
cd python-scripts
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Structure

```
python-scripts/
├── password_cracking/
│   ├── hashbreaker.py      # Concurrent version
│   ├── brute_force.py      # Single-threaded baseline
│   └── guide.md
├── ransomware/
│   ├── encrypt.py          # Encrypts files in a directory
│   ├── decrypt.py          # Decrypts them back
│   └── test/               # Test directory for trying it out
├── wordlists/
├── requirements.txt
└── README.md
```
