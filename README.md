
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
├── wordlists/
├── requirements.txt
└── README.md
```
