#!/bin/bash
set -euo pipefail

SEAWEED_VERSION="4.54"
SEAWEED_IP="${SEAWEED_IP:?}"
S3_ACCESS_KEY="${S3_ACCESS_KEY:?}"
S3_SECRET_KEY="${S3_SECRET_KEY:?}"

if ! command -v weed >/dev/null 2>&1; then
  ARCH="$(dpkg --print-architecture)"
  wget -q -O /tmp/weed.tar.gz \
    "https://github.com/seaweedfs/seaweedfs/releases/download/${SEAWEED_VERSION}/linux_${ARCH}.tar.gz"
  tar -xzf /tmp/weed.tar.gz -C /usr/local/bin weed
  rm /tmp/weed.tar.gz
fi

id seaweedfs >/dev/null 2>&1 || useradd --system --no-create-home --shell /usr/sbin/nologin seaweedfs
mkdir -p /var/lib/seaweedfs /etc/seaweedfs
chown seaweedfs:seaweedfs /var/lib/seaweedfs

cat > /etc/seaweedfs/s3.json <<EOF
{
  "identities": [
    {
      "name": "hall-app",
      "credentials": [{ "accessKey": "${S3_ACCESS_KEY}", "secretKey": "${S3_SECRET_KEY}" }],
      "actions": ["Read", "Write", "List", "Tagging", "Admin"]
    }
  ]
}
EOF
chown root:seaweedfs /etc/seaweedfs/s3.json
chmod 640 /etc/seaweedfs/s3.json

cat > /etc/systemd/system/seaweedfs.service <<EOF
[Unit]
Description=SeaweedFS (master, volume, filer, S3)
After=network-online.target
Wants=network-online.target

[Service]
User=seaweedfs
Group=seaweedfs
ExecStart=/usr/local/bin/weed server \\
  -ip=${SEAWEED_IP} \\
  -dir=/var/lib/seaweedfs \\
  -master.volumeSizeLimitMB=1024 \\
  -s3 -s3.port=8333 -s3.config=/etc/seaweedfs/s3.json
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable seaweedfs
systemctl restart seaweedfs

echo "SeaweedFS is running. S3 endpoint: http://${SEAWEED_IP}:8333"