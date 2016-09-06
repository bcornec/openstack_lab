#!/bin/sh

# Prestashop stack
#
# $1: Network ip (only class C)
# $2: Stack name (default:psstack)

cd $(dirname $0)

echo $1 | grep -qP "^\d+\.\d+\.\d+\.0$"

if [ "$?" = "0" ]
then
	net="$1/24"
	netgw=$(echo "$1" | sed 's/0$/1/')
else
	echo "Please provide a network ip ex: 10.0.1.0"
	exit 1
fi

if [ -z "$2" ]
then
	stackname="psstack"
else
	stackname="$2"
fi

# Get default security group id
default_scid=$(openstack security group show default -f json | jq .id | sed 's/"//g')
consul_scid=$(openstack security group show consulstack -f json | jq .id | sed 's/"//g')

# Create stack volume if it does not exist
openstack volume list | grep -q "$stackname"
if [ $? != 0 ]
then
	openstack volume create "$stackname" --size 2 --type "3PARGold"
	sleep 30s
fi

# Get volume id
volid=$(openstack volume show "$stackname" -f json | jq ."id" | sed 's/"//g')

# Create stack
openstack stack create  --wait -t prestashop_v5.yaml -e prestashop_v5_param.yaml --parameter \
"srvweb_name=$stackname-ha;\
srvdb_name=$stackname-db;\
default_scid=$default_scid;\
consul_scid=$consul_scid;\
private_net_name=$stackname;\
private_net_cidr=$net;\
private_net_gateway=$netgw;\
diskname=$volid"\
 $stackname
