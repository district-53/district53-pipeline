#!/bin/bash
set -euo pipefail

PKG="postgresql-client-16"

if dpkg -s "$PKG" >/dev/null 2>&1; then
  echo "${PKG} already installed"
  exit 0
fi

echo "Installing ${PKG}..."
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y "$PKG"
psql --version
