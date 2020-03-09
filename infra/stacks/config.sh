#!/bin/bash 

# 
# Configure and install packages in the bastion host.
# The default operating system is Amazon Linux 2 with the latest SSM agent installed.
#

sudo yum -y update

# Postgresql
sudo yum install -y postgresql.x86_64
