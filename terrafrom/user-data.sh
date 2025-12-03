#!/bin/bash
set -e

# Log everything
exec > >(tee /var/log/user-data.log)
exec 2>&1

echo "=== Starting Initial Setup ==="

# Update system
apt-get update
apt-get upgrade -y

# Install Python for Ansible
apt-get install -y python3 python3-pip git


# Create application directory
mkdir -p /opt/diginnocent
chown -R ubuntu:ubuntu /opt/diginnocent


echo "=== Setup Complete - Ready for Ansible ==="