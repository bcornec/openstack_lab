#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File: list_network.py
Author: René Ribaud
Email: rene.ribaud@hpe.com
Github: https://github.com/uggla
Description: Short script to list available openstack network subnets
             to provide this info to a CSA dynamic list.
"""


import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
import subprocess
import os
import sys
import re
import pprint
from openstack import connection
from openstack import utils


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="\t")

def get_command(repo, image):
    image = repo + '/' + image
    with open(os.devnull, 'w') as FNULL:
        subprocess.check_call(["docker",
                               "pull",
                               image], stdout=FNULL)
    inspect = subprocess.check_output(["docker",
                                       "inspect",
                                       image])
    inspect = json.loads(inspect)
    command = ''
    command = str(inspect[0]['Config']["Cmd"])
    if command is None:
        command=str('empty')
    else:
        command = command.replace('[u\'', '')
        command = command.replace('\']', '')
        command = command.replace('\', u\'run', '')
    return command

def get_volumes(repo, image):
    image = repo + '/' + image
    with open(os.devnull, 'w') as FNULL:
        subprocess.check_call(["docker",
                               "pull",
                               image], stdout=FNULL)
    inspect = subprocess.check_output(["docker",
                                       "inspect",
                                       image])
    inspect = json.loads(inspect)
    volumes = ''
    volumes = str(inspect[0]['Config']["Volumes"])
    if volumes is None:
        volumes=str('empty')
    else:
        volumes = volumes.replace('{u\'', '')
        volumes = volumes.replace('\': {}}', '')
    return volumes

def get_port(repo, image):
    image = repo + '/' + image
    with open(os.devnull, 'w') as FNULL:
        subprocess.check_call(["docker",
                               "pull",
                               image], stdout=FNULL)
    inspect = subprocess.check_output(["docker",
                                       "inspect",
                                       image])
    inspect = json.loads(inspect)
    port = ''
    try:
        port = inspect[0]['Config']["ExposedPorts"].keys()
        port = sorted(port)
        port = port[0].replace('/tcp', '')
    except KeyError:
        # Uggla hack to specify a port
        port = '35000'
    return port

########################################################
# Main
########################################################

utils.enable_logging(True, path='list_network.log')

# Connect to openstack and list subnets
try:
    auth_args = {
        'user_domain_name': os.environ["OS_USER_DOMAIN_NAME"],
        'project_domain_name': os.environ["OS_PROJECT_DOMAIN_NAME"],
        'auth_url': os.environ["OS_AUTH_URL"],
        'project_name': os.environ["OS_PROJECT_NAME"],
        'username': os.environ["OS_USERNAME"],
        'password': os.environ["OS_PASSWORD"],
        'verify': '/etc/ssl/certs/ca-certificates.crt'
    }
except KeyError as e:
    print("An environment variable used by Openstack is not defined")
    print(e)
    sys.exit(1)

conn = connection.Connection(**auth_args)

# for nw in conn.network.networks():
#     pprint.pprint(nw)

# Iterate on subnets, to create a list of user subnets.
# I defined user subnets as subnets between 10.1.1.0/24 and 10.1.20.0/24
user_subnets = []
for subnet in conn.network.subnets():
    check = re.match(r'\d+\.1\.(\d+)\.\d+', subnet.cidr)
    if check and 0 < int(check.group(1)) < 20:
        pprint.pprint(subnet.cidr)
        user_subnets.append(subnet.cidr)

# Build a list of available subnets
avail_subnets = []
for i in range(1, 20):
    subnet = "10.1." + str(i) + ".0/24"
    avail_subnets.append(subnet)
# pprint.pprint(avail_subnets)

# Transform list to set in order to compute differences
avail_subnets = set(avail_subnets)
user_subnets = set(user_subnets)

# pprint.pprint(avail_subnets - user_subnets)

# Create xml
root = ET.Element('Property')

for subnets in (avail_subnets - user_subnets):
    av = ET.SubElement(root, 'availableValues')
    dp = ET.SubElement(av, 'displayName')
    dp.text = "Subnet"
    desc = ET.SubElement(av, 'description')
    val = ET.SubElement(av, 'value')
    val.text = subnets
# Show output xml
print(prettify(root))

sys.exit(0)
