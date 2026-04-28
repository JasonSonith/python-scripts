import xml.etree.ElementTree as ET 

file = 'nmap.xml'
tree = ET.parse(file)
root = tree.getroot()

scan = {'ip_address': None}

for elm in root.findall('.//'):
	print(f"Tag = {elm.tag}")
	print(f"Attribute={elm.attrib}\n")

# 	if elm.tag == 'address':
# 		attribute = elm.attrib

ports = {}

for elm in root.findall('.//port'):

	port = int(elm.get('portid'))
	ports[port] = {}
	ports[port]['service_name'] = elm.find('service').get('name')

print(ports)
