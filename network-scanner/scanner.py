import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import socket

parser = argparse.ArgumentParser(description='Network scanner that determines the status of ports of remote computers')
parser.add_argument('--target', type = str, default = '45.33.32.156', required = False, help = "Target IP address (Example: 192.100.12.1)")
parser.add_argument('--ports', type = str, default = '1-1000', required = False, help= "Range of ports (Example: 1-1000)")
args = parser.parse_args()

target = args.target
port_range = args.ports
start, end = port_range.split('-')
start,end = int(start), int(end)

def Scanner(target, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(2)
    
    try:
        client.connect((target, port))
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
        
        return None
    
    except ConnectionRefusedError:
        print(f"Port {port}: closed")
        return None
    
    except Exception as e:
        print(f"Error on port {port}: {e}")
        return None
    
    finally:
        client.close()

def main():
    ports = [port for port in range (start, end + 1)]
    responses = {}
    
    with ThreadPoolExecutor(max_workers= os.cpu_count()) as executor:
        future_ports = {executor.submit(Scanner, target, port) for port in ports}

        for future in as_completed(future_ports):
            result = future.result()
            
            if result is not None:
                port_num, response = result
                responses[port_num] = response
        
        for port, response in sorted(responses.items()):
            if responses:
                print(f"Response on port {port}: {response}")
            else:
                print(f"No open ports found")
        
        
if __name__ == '__main__':
    main()