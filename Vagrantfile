# Vagrantfile to spin up a VM for the ChatGPT Agent environment
# Usage: vagrant up && vagrant ssh
Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/jammy64"
  config.vm.hostname = "chatgpt-agent-vm"

  # Network
  config.vm.network "private_network", type: "dhcp"

  # Forward agent port (if agent exposes a web UI)
  config.vm.network "forwarded_port", guest: 8080, host: 8080, auto_correct: true

  # Provisioning with shell script
  config.vm.provision "shell", path: "./scripts/provision.sh"

  # Sync folders for workspace
  config.vm.synced_folder ".", "/home/vagrant/workspace", type: "rsync", rsync__auto: true

  # Increase memory for heavier tasks
  config.vm.provider "virtualbox" do |vb|
    vb.memory = "4096"
    vb.cpus = 2
  end
end
