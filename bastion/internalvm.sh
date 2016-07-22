#!/bin/bash

openstack server create --flavor m1.small --image "Debian Jessie 64-bit" --key-name bastionkey --nic net-id=private internalvm
vmip=""

while [ -z "$vmip" ]
do
	vmip=$(openstack server show internalvm -f json | jq .addresses | perl -pe 's#.*[\s=](\d+\.\d+\.\d+\.\d+).*#\1#g' | sed 's/"//g')
	sleep 5s
done

echo "VM ip $vmip"
