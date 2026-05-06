import subprocess
import xml.etree.ElementTree as ET
import argparse
import sys
import requests
import re
from pathlib import Path
from urllib.parse import urlparse
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

parser = argparse.ArgumentParser(description="Automated web enumeration tool")
parser.add_argument('-i','--ip', required=True)
args = parser.parse_args()
ip = args.ip

class WebEnumeration:

    def __init__(self,ip):
        self.ip = ip

    def run_nmap(self, ip: str):
        Path('nmap').mkdir(exist_ok=True)
        subprocess.run(['nmap', '-p-', '--min-rate', '1000', '-T4', '-oA', 'tcp_full', f'{ip}'], check=True)
        file = 'tcp_full.xml'
        tree = ET.parse(file)
        root = tree.getroot()

        ports = {}
        open_ports = [] 

        try:
            for elm in root.findall('.//port'):
                port = (elm.get('portid'))

                if port:
                    state = elm.find('state')

                    if state is not None and state.get('state') == 'open':
                        open_ports.append(elm.get('portid'))
            if open_ports:
                subprocess.run(['nmap', '-p', ','.join(open_ports), '-sCV', '-oA', 'nmap/tcp_services', f'{ip}'], check=True)

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

        except Exception as e:
            print('[+] Error: could not parse XML tree')
            sys.exit(1)

        return ports


    def run_gobuster(self, ip: str, ports: dict):
        port = None

        for key, value in ports.items():
            if 'http' in value['service_name']:
                port = key
                print(f"[+] {value['service_name']} found in port {key}")
                break

        if port is not None:
            domain = self._get_vhost_domain(ip)
            is_vhost, length_host = self._check_vhost(domain)

            if not is_vhost:
               print('[+] Skipping vhost mode for gobuster...') 

            else:
                # VHOST COMMANDS
                try:
                    Path('gobuster').mkdir(exist_ok=True)
                    wordlist = '/usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt'
                    vhost_cmd = ['gobuster', 'vhost', '-u', f'http://{domain}','-w', f'{wordlist}', '--append-domain', '-fs', f'{length_host}', '-o', 'vhost/vhost.txt']
                    subprocess.run(vhost_cmd, check=True)
                    vhost_file = Path('vhost/vhost.txt')
                    valid_hosts = self._get_vhost_pattern(vhost_file)

                    for host in valid_hosts:
                        with open('/etc/hosts', 'a') as f:
                            f.write(f'{ip} {host}\n')

                except Exception as e:
                    print("[+] Error: Could not process vhost command...")
                    sys.exit(1)
            
            # DIR COMMANDS
            wordlist = "/usr/share/wordlists/dirb/common.txt"
            dir_cmd = ['gobuster', 'dir', '-u', f'{domain}{port}', '-w', f'{wordlist}', '-x', "php,txt,html", '-o', 'gobuster/dirbuster.txt']

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
    
    def _get_vhost_domain(self, ip):
        try:
            r = requests.get(f'http://{ip}', allow_redirects=False, timeout=5)
            location = r.headers.get('Location', '')
            if location:
                parsed = urlparse(location)
                return parsed.hostname
        except requests.RequestException:
            print("[+]No vhost domain found...")
        return None

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
    enum = WebEnumeration(ip)
    ports = enum.run_nmap(ip)
    enum.run_gobuster(ip, ports)

if __name__ == '__main__':
    main()
