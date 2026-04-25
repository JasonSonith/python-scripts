import subprocess
import pathlib
import xml.etree.ElementTree as ET
import argparse
import sys


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

    def run_nmap(self, ip):
        subprocess.run('nmap -sC -sV -p- -oX nmap.xml -oN nmap.txt {ip}')
        file = 'nmap.xml'
        tree = ET.parse(file)
        root = tree.getroot()

        ports = {}

        try:
            for elm in root.findall('.//port'):
                port = int(elm.get('portid'))
                ports[port] = {}

                if elm.find('service') is not None:
                    ports[port]['service name'] = elm.find('service').get('name')
                    ports[port]['product'] = elm.find('service').get('product')
                    ports[port]['version'] = elm.find('service').get('version')

                if elm.find('state') is not None:
                    ports[port]['state'] = elm.find('state').get('state')


        except Exception as e:
            print('[+] Error: could not parse XML tree')

            return ports


    def run_gobuster(self):
        pass

    def run_ffuf(self):
        pass

    def run_hashcat(self):
        pass

def main():
    enum = WebEnumeration()
    enum.run_nmap(ip)

if __name__ == '__main__':
    main()