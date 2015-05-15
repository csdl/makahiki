#!/usr/bin/env bash
# Create file timestamp
FNAME="ubuntu_x86_"
TIMESTAMP=$(date +"%Y-%m-%d-%H-%M-%S")
FNAME2="$FNAME$TIMESTAMP.log"
# Run installation script
sudo sh /vagrant/bootstrap.sh | tee "/vagrant/vagrant/logs/$FNAME2"

