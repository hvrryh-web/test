# VM Connection Guide

Connect via Vagrant:

- On your host machine:

```
# Start the VM
vagrant up

# Connect to the VM via SSH
vagrant ssh
```

If you prefer to connect via a standard SSH client:

1. Inspect Vagrant's SSH config:
```
vagrant ssh-config
```
2. Use the printed HostName, Port, IdentityFile, and User to connect:
```
ssh -i /path/to/identityfile -p <port> vagrant@<hostname>
```

Or connect as the agent user inside the VM:

```
# From inside the VM
sudo -u agent -i
```

This environment syncs the workspace into the VM at `/home/vagrant/workspace` so agent code and resources are accessible.
