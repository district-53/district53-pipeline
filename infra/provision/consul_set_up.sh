#!/bin/bash
set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

if ! command -v consul >/dev/null 2>&1; then
  apt-get update -y
  apt-get install -y wget gpg lsb-release

  wget -O - https://apt.releases.hashicorp.com/gpg \
    | gpg --batch --yes --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg

  echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" \
    > /etc/apt/sources.list.d/hashicorp.list

  apt-get update -y
  apt-get install -y consul
fi

install -o consul -g consul -m 640 /tmp/consul.hcl /etc/consul.d/consul.hcl

consul validate /etc/consul.d/

systemctl enable consul
systemctl restart consul

echo "Consul server is running. UI: http://192.168.56.12:8500"