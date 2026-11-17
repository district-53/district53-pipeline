#!/bin/bash

#Add user admin
useradd -m -s /bin/bash "$ADMIN_USER"
usermod -p '*' "$ADMIN_USER"

SUDO_FILE="/etc/sudoers.d/90-$ADMIN_USER"
echo "$ADMIN_USER ALL=(ALL) NOPASSWD:ALL" > "$SUDO_FILE"
chmod 440 "$SUDO_FILE"


HOME_DIR=$(getent passwd "$ADMIN_USER" | cut -d: -f6)
install -d -m 700 -o "$ADMIN_USER" -g "$ADMIN_USER" "$HOME_DIR/.ssh"
echo "$ADMIN_PUBKEY" > "$HOME_DIR/.ssh/authorized_keys"
chown "$ADMIN_USER:$ADMIN_USER" "$HOME_DIR/.ssh/authorized_keys"
chmod 600 "$HOME_DIR/.ssh/authorized_keys"


#root off password awtorization
passwd -l root >/dev/null

cat > /etc/ssh/sshd_config.d/00-users_set_up.conf <<'EOF'
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
EOF
chmod 644 /etc/ssh/sshd_config.d/00-users_set_up.conf


systemctl reload ssh 2>/dev/null || systemctl reload sshd