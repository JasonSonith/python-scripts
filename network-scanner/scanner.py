import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
import os
from rich.progress import Progress
import socket
import time

parser = argparse.ArgumentParser(description='Network scanner that determines the status of ports of remote computers')
parser.add_argument('--target', type = str, default = '45.33.32.156', required = False, help = "Target IP address (Example: 192.100.12.1)")
parser.add_argument('--ports', type = str, default = '1-1000', required = False, help= "Range of ports (Example: 1-1000)")
parser.add_argument('--timeout', type = float, default = 2.0, required = False, help = 'Timeout for communication with ports')
parser.add_argument('--threads', type = int, default = os.cpu_count(), required = False, help = 'Number of threads to execute')
args = parser.parse_args()

target = args.target
port_range = args.ports
timeout = args.timeout
thread_count = args.threads
start, end = port_range.split('-')
start,end = int(start), int(end)
errors = defaultdict(int)

class Scanner:
    def __init__(self, target, port_range):
        self.target = target
        self.port_range = port_range
        self.ports = [port for port in range(start, end + 1)]
    
    def tcp_grab_banner(self, port):
        global errors
        
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(timeout)
        
        try:
            client.connect((self.target, port))
            
            try:
                response = client.recv(4096).decode().strip()
                
                if response:
                    return port, response
            
            except socket.timeout:
                pass
            
            client.send('HEAD / HTTP/1.1\r\nHost: host\r\n\r\n'.encode())
            response = client.recv(4096).decode().strip()
            
            if response:
                return port, response

        except Exception as e:
            errors[type(e).__name__] += 1
            return None

        finally:
            client.close()
        
            
    def scan(self):
        tcp_responses = {}
        udp_responses = {}

        with Progress() as progress:
            task = progress.add_task("[cyan]Scanning...", total = len(self.ports) * 2)
            
            with ThreadPoolExecutor(max_workers= thread_count) as executor:
                tcp_future_ports = [executor.submit(self.tcp_grab_banner, port) for port in self.ports]
                udp_future_ports = [executor.submit(self.udp_grab_banner, port) for port in self.ports]
                
                for future in as_completed( tcp_future_ports + udp_future_ports):
                    result = future.result()
                    progress.update(task,advance=1)

                    if result:
                        port, response = result
                        
                        if future in tcp_future_ports:
                            tcp_responses[port] = response
                            
                        else:
                            udp_responses[port] = response
                            
        if tcp_responses:
            for port, response in tcp_responses.items():
                print(f"  {port}: {response}")
    
        if udp_responses:
            for port, response in udp_responses.items():
                print(f"  {port}: {response}")
    
        if not tcp_responses and not udp_responses:
            print("No open ports found")

    if errors:
        for error, value in errors.items():
            print(f"{error}: {value} port(s)")
    
    def udp_grab_banner(self, port):
        global errors
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client.settimeout(timeout)
        
        probes = {
        53: b'\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00',  # DNS
        123: b'\x1b' + 47 * b'\x00',  # NTP
        161: b'\x30\x26\x02\x01\x01\x04\x06public',  # SNMP
        }
    
        probe = probes.get(port, b'\x00')

        try:
            client.sendto(probe, (self.target, port))
            response, addr = client.recvfrom(4096)
            response = response.decode(errors = 'ignore').strip()
            
            if response:
                return port, response
            
        except socket.timeout:
            return None
    
        except Exception as e:
            errors[type(e).__name__] += 1
            return None
        
        finally:
            client.close()

def main():
    scanner = Scanner(target, port_range)
    scanner.scan()

if __name__ == '__main__':
    main()