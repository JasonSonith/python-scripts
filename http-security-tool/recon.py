import argparse
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.progress import Progress
import requests
from requests.structures import CaseInsensitiveDict
import urllib3

parser = argparse.ArgumentParser(description = 'HTTP Security Tool')
parser.add_argument('--url', type = str, required = True, help = 'URL for security recon')
args = parser.parse_args()
url = args.url

#variables for checking security headers found or not found

def check_headers(url):
    found_headers = 0
    missing_headers = 0

    #try statements attempts to check which headers are and aren't avaliable
    try:
        response = requests.get(url)
        headers = response.headers
        print(f"SECURITY HEADER FOR {url}")
        
        security_headers = [
            'Content-Security-Policy',
            'Strict-Transport-Security',
            'X-Content-Type-Options',
            'X-Frame-Options',
            'Referrer-Policy',
            'Permissions-Policy',
            'Clear-Site-Data',
            'Cross-Origin-Embedder-Policy',
            'Cross-Origin-Resource-Policy'
        ]
        
        for header in security_headers:
            
            if header in headers:
                print(f"Found {header}: {headers[header]}")
                found_headers += 1
            
            else:
                print(f"{header}: not found")
                missing_headers += 1
                
    except requests.exceptions.RequestException as e:
        print(f"Error accessing {url}: {e}")
    
    print(f"Found {found_headers} headers")
    print(f"Missing {missing_headers} headers")
    print('=' * 30)

#checks misconfigured cross-origin resource sharing
def check_cors(url):
    
    headers = {
        'Origin': 'https://evil.com'
    }
    
    response = requests.get(url, headers = headers)
    cors = response.headers.get('Access-Control-Allow-Origin')
    
    misconfigured_cors = ['*', headers['Origin'], 'null']
    
    if cors in misconfigured_cors:
        print(f'Misconfigured origin: {cors}')
        
    elif cors:
        print(f'CORS: {cors}')
    else:
        print('No CORS headers')

def main():
    check_headers(url)
    check_cors(url)

if __name__ == '__main__':
    main()