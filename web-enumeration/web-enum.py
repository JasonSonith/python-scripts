import subprocess
import xml.etree.ElementTree as ET
import argparse
import sys
import requests
import re
from pathlib import Path

parser = argparse.ArgumentParser(description="Automated web enumeration tool")
parser.add_argument('-ip', type=str, required=True)

try:
    args = parser.parse_args()
    ip = args.ip()

except Exception as e:
    print("[+] Error: No valid IP address passed in.\n Exiting Program...")
    sys.exit()

class WebEnumeration:

    def __init__(self):
        self.ip = ip

    def run_nmap(self, ip: str):
        subprocess.run(['nmap', '-sC', '-sV', '-p-','-oX', 'nmap.xml', '-oN', 'nmap.txt', f'{ip}'], check=True)
        file = 'nmap.xml'
        tree = ET.parse(file)
        root = tree.getroot()

        ports = {}

        try:
            for elm in root.findall('.//port'):
                port = (elm.get('portid'))

                if port:
                    port = int(port)

                ports[port] = {}
                service = elm.find('service')

                if service is not None:
                    ports[port]['service_name'] = service.get('name')
                    ports[port]['product'] = service.get('product')
                    ports[port]['version'] = service.get('version')

                state = elm.find('state')
                if state is not None:
                    ports[port]['state'] = state.get('state')


        except Exception as e:
            print('[+] Error: could not parse XML tree')
            sys.exit()

        return ports


    def run_gobuster(self, ip: str, ports: dict):
        port = None

        for key, value in ports.items():
            if 'http' in value['service_name']:
                port = key
                print(f"[+] {value['service_name']} found in port {key}")
                break

        if port is not None:
            url = f"http://{ip}:{port}"
            is_vhost, len =self._check_vhost(url)

            if not is_vhost:
                pass

            else:
                # VHOST COMMANDS
                try:
                    wordlist = '/usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt'
                    vhost_cmd = ['gobuster', 'vhost', '-u', f'{url}', '-H', f'Host: FUZZ{url}', '-fs', f'{len}', '-o', 'vhost.txt']
                    subprocess.run(vhost_cmd, check=True)

                    # Need to add DNS to /etc/host
                    vhost_file = Path('vhost.txt')
                    subprocess.run(['echo', f'"{ip}'])

                except Exception as e:
                    print("[+] Error: Could not process vhost command...")
                    sys.exit()
            
            # DIR COMMANDS
            wordlist = "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt"
            dir_cmd = ['gobuster', 'dir', '-u', f'{url}', '-w', f'{wordlist}', '-x', 'php,txt,html', '-o', 'dirbuster.txt']

            if port == 443:
                dir_cmd.append('-k')

            subprocess.run(dir_cmd, check=True)
            return

    def _check_vhost(self, url):
        real_url = requests.get(url, verify = False, timeout = 10)
        fake_url = requests.get(url, headers = {"Host": "fake.site"},verify = False, timeout = 10)

        if len(real_url.content) == len(fake_url.content) and real_url.status_code == fake_url.status_code:
            return False, None

        return True, len(real_url.content)

    def _get_vhost_pattern(self,file):
        vhost_pattern = re.compile(r'Found:\s+(?P<host>\S+)\s+')
        results = []

        with open(file, 'r', encoding='utf-8') as f:
            for line in f.read().splitlines():
                if 'Found:' in line.strip():
                    match = vhost_pattern.search(line)
                    
                    if match:
                        results.append(match['host'])

            return results
                    

def main():
    enum = WebEnumeration()
    ports = enum.run_nmap(ip)
    enum.run_gobuster(ip, ports)

if __name__ == '__main__':
    main()
