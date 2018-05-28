# ansible-sshlxd-connection

Use the ssh client library to access the LXD host and then use lxc commands to interact with the container.

By using the ssh connection, only port ssh port is required to be open. Also no need to configure LXD to allow remote connections. 

## Requirements

Machine running ansible:

* Ansible 2.5+ and its dependencies

Host:

* LXD, tested with the version Ubuntu Xenial(16.04.1)
* ssh
* sudo
* python 2.7

LXD container:

* python 2.7

## Installing

Add the file sshlxd.py to the `connection_plugins/` directory.
The path to the `connection_plugins/` directory can be set via `ansibile.cfg` file:

```
[defaults]
...
connection_plugins = connection_plugins
...
```

## Using

Add the an entry to the inventory as per the example:
```
[container]
alpine1@127.0.0.1 ansible_ssh_port=22 ansible_connection=sshlxd ansible_ssh_user=ubuntu
```

The use your plays as usual:
```
---
- hosts: container  
  tasks:
  - name: Just checking sshlxd!
    ping:
```

To give `sshlxd` the privileges it needs to `lxd exec`, you have to use `become: true` in the play for the container, or add the `ansible_ssh_user` to the LXD group on the remote host.

## Credit

This version is forked from Andreas Fuchs (@antifuchs) https://github.com/antifuchs/ansible-sshlxd-connection.git , mainly to offer ansible 2.5 compatibility. 

### From the original author Andreas Fuchs (@antifuchs)
_This plugin owes pretty much everything to
[ansible-sshjail](https://github.com/austinhyde/ansible-sshjail) - it
started life as a copy of that code (and still retains most of its
heritage!). Thanks to @austinhyde for making this!_
