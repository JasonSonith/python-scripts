import subprocess
import pathlib
import xml.etree.ElementTree as ET
import argparse
import sys
import requests


parser = argparse.ArgumentParser(description="Automated web enumeration tool")
parser.add_argument('-ip', type=str, required=True)

try:
    args = parser.parse_args()

except Exception as e:
    print(f"[+] Error: No valid IP address passed in.\n Exiting Program...")

ip = args.ip()

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
                port = int(elm.get('portid'))
                ports[port] = {}

                if elm.find('service') is not None:
                    ports[port]['service_name'] = elm.find('service').get('name')
                    ports[port]['product'] = elm.find('service').get('product')
                    ports[port]['version'] = elm.find('service').get('version')

                if elm.find('state') is not None:
                    ports[port]['state'] = elm.find('state').get('state')


        except Exception as e:
            print('[+] Error: could not parse XML tree')

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
            is_vhost =self._check_vhost(url)
            if not is_vhost:
                pass

            # VHOST COMMANDS
            #LEFT OFF HERE: CREATE VHOST CMDS

            # DIR COMMANDS
            wordlist = "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt"
            mode = "dir"
            dir_cmd = ['gobuster', 'dir', '-u', f'{url}', '-w', f'{wordlist}', '-x', 'php,txt,html', '-o', 'dirbuster.txt']

            if port == 443:
                dir_cmd.append('-k')

            subprocess.run(dir_cmd, check=True)
            return

        def _check_vhost(self, url):
            real_url = requests.get(url, verify = False, timeout = 10)
            fake_url = requests.get(url, headers = {"Host": "fake.site"},verify = False, timeout = 10)

            if len(real_url.content) == len(fake_url.content) and real_url.status_code == fake_url.status_code:
                return False

            return True

def main():
    enum = WebEnumeration()
    ports = enum.run_nmap(ip)
    enum.run_gobuster(ip, ports)

if __name__ == '__main__':
    main()
