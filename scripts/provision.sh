#!/usr/bin/env bash
set -eux

# System updates
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get -y upgrade

# Install common packages
DEBIAN_FRONTEND=noninteractive apt-get -y install python3 python3-pip python3-venv git curl unzip openssh-server rsync build-essential vim
# Docker & docker-compose for container-based sandboxing
DEBIAN_FRONTEND=noninteractive apt-get -y install ca-certificates gnupg lsb-release
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update && apt-get -y install docker-ce docker-ce-cli containerd.io
pip install docker-compose

# Create agent user and setup SSH
AGENT_USER="agent"
if ! id -u "$AGENT_USER" >/dev/null 2>&1; then
  useradd -m -s /bin/bash "$AGENT_USER"
  echo "$AGENT_USER ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$AGENT_USER
fi

# Setup Python virtualenv
sudo -u "$AGENT_USER" bash -lc "python3 -m venv /home/$AGENT_USER/venv"

# Install project requirements if present
PROJECT_DIR="/home/vagrant/workspace"
if [ -f "$PROJECT_DIR/requirements.txt" ]; then
  echo "Installing Python requirements..."
  sudo -u "$AGENT_USER" bash -lc "source /home/$AGENT_USER/venv/bin/activate && pip install --upgrade pip && pip install -r $PROJECT_DIR/requirements.txt"
fi

# Create initial directories and sample SSH key for agent user if none exist
if [ ! -d "/home/$AGENT_USER/.ssh" ]; then
  sudo -u "$AGENT_USER" mkdir -p /home/$AGENT_USER/.ssh
  sudo -u "$AGENT_USER" ssh-keygen -t ed25519 -N '' -f /home/$AGENT_USER/.ssh/id_ed25519
fi

# Setup a service unit (optional) to run the agent harness
cat >/etc/systemd/system/agent-harness.service <<'EOF'
[Unit]
Description=ChatGPT Agent Harness Service
After=network.target

[Service]
Type=simple
User=agent
WorkingDirectory=/home/vagrant/workspace
<<<<<<< Updated upstream
ExecStart=/home/agent/venv/bin/python /home/vagrant/workspace/agent/agent_runner.py --watch
=======
ExecStart=/home/agent/venv/bin/python -m agent.agent_runner --watch
>>>>>>> Stashed changes
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload || true

# Add agent user to docker group so it can run docker commands without sudo
if command -v docker >/dev/null 2>&1; then
  groupadd -f docker || true
  usermod -aG docker "$AGENT_USER"
  # Optionally run docker-compose to start local services
  if [ -f "/home/vagrant/workspace/docker-compose.yml" ]; then
    sudo -u "$AGENT_USER" bash -lc "cd /home/vagrant/workspace && docker compose up -d --build"
  fi
fi

# Final message
echo "Provisioning complete. Connect via 'vagrant ssh' or configure SSH to the agent user on the VM." 
