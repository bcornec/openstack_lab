#!/bin/bash

openstack keypair create --public-key ~/.ssh/id_rsa.pub bastionkey  # add pub key from host
nova boot --image "Debian Jessie 64-bit" --flavor m1.small --key bastionkey --nic net-name=private bastion  # Create instance
pubip=$(openstack ip floating create -f json ext-net | jq .floating_ip_address | sed 's/"//g')  # Allocate an ip in pool
openstack ip floating add "$pubip" bastion  # Associate the ip to the instance
echo "VM should be accessible soon at $pubip"

while ! ssh-keyscan $pubip
do
	sleep 5s
done

ssh-keyscan $pubip >> ~/.ssh/known_hosts
