"""utility methods for AWS"""

import boto.ec2
import boto
import os
from boto.s3.key import Key

aws_region = 'us-west-2'
aws_image_id = 'ami-e7527ed7'
aws_instance_type = 't2.micro'

makahiki_user_data = """#!/bin/bash
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

EC2_connection = boto.ec2.connect_to_region(aws_region,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key)

S3_connection = boto.connect_s3(aws_access_key_id, aws_secret_access_key)


def create_bucket(bucket):
    S3_connection.create_bucket(bucket)

def delete_bucket(bucket):
    b = S3_connection.get_bucket(bucket)
    for key in b.list():
        print 'deleting %s' % key
        key.delete()

    # The bucket is empty now. Delete it.
    S3_connection.delete_bucket(bucket)

def get_key(bucket, key):
    b = S3_connection.get_bucket(bucket)
    k = Key(b)
    k.key = key
    return k

def list_all():
    rs = S3_connection.get_all_buckets()
    for b in rs:
        print b.name

def download(bucket):
    b = S3_connection.get_bucket(bucket)
    rs = b.list()
    for key in rs:
        k.get_contents_to_filename(key.name)

def put_string(bucket, key, string_value):
    k = get_key(bucket, key)
    k.set_contents_from_string(string_value)

def get_string(bucket, key):
    k = get_key(bucket, key)
    return k.get_contents_as_string()

def put_file(bucket, key, in_filename):
    k = get_key(bucket, key)
    k.set_contents_from_filename(in_filename)

def get_file(bucket, key, out_filename):
    k = get_key(bucket, key)
    k.get_contents_to_filename(out_filename)


def launch_instance(makahiki=None):
    interface = boto.ec2.networkinterface.NetworkInterfaceSpecification(
            subnet_id=aws_subnet_id,
            groups=[aws_security_group_id,],
            associate_public_ip_address=True)

    interfaces = boto.ec2.networkinterface.NetworkInterfaceCollection(interface)


    if makahiki:
        user_data = makahiki_user_data
    else:
        user_data = None

    reservation = EC2_connection.run_instances(aws_image_id,
                       key_name=aws_key_name,
                       instance_type=aws_instance_type,
                       network_interfaces=interfaces,
                       user_data=user_data)
    print reservation.instances;

def stop_instances(instance_id):
    EC2_connection.stop_instances(instance_ids=[instance_id,])

def status():
    statuses = EC2_connection.get_all_instance_status(include_all_instances=True)

    print statuses
    for status in statuses:
        print "%s - %s - %s - %s" % (status.id, status.state_name, status.events, status.system_status)
