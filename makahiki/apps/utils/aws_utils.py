"""utility methods for AWS"""

import boto.ec2
import os

aws_region = 'us-west-2'
aws_image_id = 'ami-e7527ed7'
aws_instance_type = 't2.micro'
aws_user_data = """#!/bin/bash
yum install -y docker
service docker start
pip install docker-compose
yum install -y git
git clone https://github.com/csdl/makahiki
cd makahiki
/usr/local/bin/docker-compose build
/usr/local/bin/docker-compose pull db
/usr/local/bin/docker-compose start db
sleep 2
/usr/local/bin/docker-compose run web python makahiki/scripts/initialize_instance.py -t default -d
/usr/local/bin/docker-compose up -d
"""

aws_access_key_id = os.environ['MAKAHIKI_AWS_ACCESS_KEY_ID']
aws_secret_access_key = os.environ['MAKAHIKI_AWS_SECRET_ACCESS_KEY']
aws_subnet_id = os.environ['MAKAHIKI_AWS_SUBNET_ID']
aws_security_group_id = os.environ['MAKAHIKI_AWS_SECURITY_GROUP_ID']
aws_key_name = os.environ['MAKAHIKI_AWS_KEY_NAME']

conn = boto.ec2.connect_to_region(aws_region,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key)


def launch_instance():
    interface = boto.ec2.networkinterface.NetworkInterfaceSpecification(
            subnet_id=aws_subnet_id,
            groups=[aws_security_group_id,],
            associate_public_ip_address=True)

    interfaces = boto.ec2.networkinterface.NetworkInterfaceCollection(interface)


    reservation = conn.run_instances(aws_image_id,
                       key_name=aws_key_name,
                       instance_type=aws_instance_type,
                       network_interfaces=interfaces,
                       user_data=aws_user_data)
    print reservation.instances;

def stop_instances(instance_id):
    conn.stop_instances(instance_ids=[instance_id,])

def status():
    statuses = conn.get_all_instance_status(include_all_instances=True)

    print statuses
    for status in statuses:
        print "%s - %s - %s - %s" % (status.id, status.state_name, status.events, status.system_status)
