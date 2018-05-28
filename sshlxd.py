from __future__ import (absolute_import, division, print_function)
import os
import os.path
import pipes

from ansible.errors import AnsibleError
from ansible.plugins.connection.ssh import Connection as SSHConnection
from contextlib import contextmanager

__metaclass__ = type

DOCUMENTATION = '''
    connection: ssh
    short_description: connect to LXD containers using lxc comand via ssh client binary
    description:
        - Use the ssh client library to access the LXD host and then use lxc commands to interact with the container.
        - Options are the same as ssh, except got host variable wich should be <container_name>@<host>
    author: Andreas Fuchs (@antifuchs), Joao Silva(@wnke)
    version_added: historical
    options:
      host:
          description: Hostname/ip to connect to.
          default: inventory_hostname
          vars:
               - name: container@ansible_host
               - name: container@ansible_ssh_host
      host_key_checking:
          description: Determines if ssh should check host keys
          type: boolean
          ini:
              - section: defaults
                key: 'host_key_checking'
              - section: ssh_connection
                key: 'host_key_checking'
                version_added: '2.5'
          env:
              - name: ANSIBLE_HOST_KEY_CHECKING
              - name: ANSIBLE_SSH_HOST_KEY_CHECKING
                version_added: '2.5'
          vars:
              - name: ansible_host_key_checking
                version_added: '2.5'
              - name: ansible_ssh_host_key_checking
                version_added: '2.5'
      password:
          description: Authentication password for the C(remote_user). Can be supplied as CLI option.
          vars:
              - name: ansible_password
              - name: ansible_ssh_pass
      ssh_args:
          description: Arguments to pass to all ssh cli tools
          default: '-C -o ControlMaster=auto -o ControlPersist=60s'
          ini:
              - section: 'ssh_connection'
                key: 'ssh_args'
          env:
              - name: ANSIBLE_SSH_ARGS
      ssh_common_args:
          description: Common extra args for all ssh CLI tools
          vars:
              - name: ansible_ssh_common_args
      ssh_executable:
          default: ssh
          description:
            - This defines the location of the ssh binary. It defaults to `ssh` which will use the first ssh binary available in $PATH.
            - This option is usually not required, it might be useful when access to system ssh is restricted,
              or when using ssh wrappers to connect to remote hosts.
          env: [{name: ANSIBLE_SSH_EXECUTABLE}]
          ini:
          - {key: ssh_executable, section: ssh_connection}
          #const: ANSIBLE_SSH_EXECUTABLE
          version_added: "2.2"
      sftp_executable:
          default: sftp
          description:
            - This defines the location of the sftp binary. It defaults to `sftp` which will use the first binary available in $PATH.
          env: [{name: ANSIBLE_SFTP_EXECUTABLE}]
          ini:
          - {key: sftp_executable, section: ssh_connection}
          version_added: "2.6"
      scp_executable:
          default: scp
          description:
            - This defines the location of the scp binary. It defaults to `scp` which will use the first binary available in $PATH.
          env: [{name: ANSIBLE_SCP_EXECUTABLE}]
          ini:
          - {key: scp_executable, section: ssh_connection}
          version_added: "2.6"
      scp_extra_args:
          description: Extra exclusive to the 'scp' CLI
          vars:
              - name: ansible_scp_extra_args
      sftp_extra_args:
          description: Extra exclusive to the 'sftp' CLI
          vars:
              - name: ansible_sftp_extra_args
      ssh_extra_args:
          description: Extra exclusive to the 'ssh' CLI
          vars:
              - name: ansible_ssh_extra_args
      retries:
          # constant: ANSIBLE_SSH_RETRIES
          description: Number of attempts to connect.
          default: 3
          type: integer
          env:
            - name: ANSIBLE_SSH_RETRIES
          ini:
            - section: connection
              key: retries
            - section: ssh_connection
              key: retries
      port:
          description: Remote port to connect to.
          type: int
          default: 22
          ini:
            - section: defaults
              key: remote_port
          env:
            - name: ANSIBLE_REMOTE_PORT
          vars:
            - name: ansible_port
            - name: ansible_ssh_port
      remote_user:
          description:
              - User name with which to login to the remote server, normally set by the remote_user keyword.
              - If no user is supplied, Ansible will let the ssh client binary choose the user as it normally
          ini:
            - section: defaults
              key: remote_user
          env:
            - name: ANSIBLE_REMOTE_USER
          vars:
            - name: ansible_user
            - name: ansible_ssh_user
      pipelining:
          default: ANSIBLE_PIPELINING
          description:
            - Pipelining reduces the number of SSH operations required to execute a module on the remote server,
              by executing many Ansible modules without actual file transfer.
            - This can result in a very significant performance improvement when enabled.
            - However this conflicts with privilege escalation (become).
              For example, when using sudo operations you must first disable 'requiretty' in the sudoers file for the target hosts,
              which is why this feature is disabled by default.
          env:
            - name: ANSIBLE_PIPELINING
            #- name: ANSIBLE_SSH_PIPELINING
          ini:
            - section: defaults
              key: pipelining
            #- section: ssh_connection
            #  key: pipelining
          type: boolean
          vars:
            - name: ansible_pipelining
            - name: ansible_ssh_pipelining
      private_key_file:
          description:
              - Path to private key file to use for authentication
          ini:
            - section: defaults
              key: private_key_file
          env:
            - name: ANSIBLE_PRIVATE_KEY_FILE
          vars:
            - name: ansible_private_key_file
            - name: ansible_ssh_private_key_file
      control_path:
        description:
          - This is the location to save ssh's ControlPath sockets, it uses ssh's variable substitution.
          - Since 2.3, if null, ansible will generate a unique hash. Use `%(directory)s` to indicate where to use the control dir path setting.
        env:
          - name: ANSIBLE_SSH_CONTROL_PATH
        ini:
          - key: control_path
            section: ssh_connection
      control_path_dir:
        default: ~/.ansible/cp
        description:
          - This sets the directory to use for ssh control path if the control path setting is null.
          - Also, provides the `%(directory)s` variable for the control path setting.
        env:
          - name: ANSIBLE_SSH_CONTROL_PATH_DIR
        ini:
          - section: ssh_connection
            key: control_path_dir
      sftp_batch_mode:
        default: 'yes'
        description: 'TODO: write it'
        env: [{name: ANSIBLE_SFTP_BATCH_MODE}]
        ini:
        - {key: sftp_batch_mode, section: ssh_connection}
        type: bool
      scp_if_ssh:
        default: smart
        description:
          - "Prefered method to use when transfering files over ssh"
          - When set to smart, Ansible will try them until one succeeds or they all fail
          - If set to True, it will force 'scp', if False it will use 'sftp'
        env: [{name: ANSIBLE_SCP_IF_SSH}]
        ini:
        - {key: scp_if_ssh, section: ssh_connection}
      use_tty:
        version_added: '2.5'
        default: 'yes'
        description: add -tt to ssh commands to force tty allocation
        env: [{name: ANSIBLE_SSH_USETTY}]
        ini:
        - {key: usetty, section: ssh_connection}
        type: bool
        yaml: {key: connection.usetty}
'''


try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display
    display = Display()


class ConnectionBase(SSHConnection):
    pass


class Connection(ConnectionBase):
    ''' ssh based connections '''

    transport = 'sshlxd'

    def __init__(self, *args, **kwargs):
        super(Connection, self).__init__(*args, **kwargs)

        self.inventory_hostname = self.host
        self.containerspec, self.host = self.host.split('@', 1)

        self.connector = None

    def get_container_id(self):
        return self.containerspec

    def get_container_connector(self):
        return 'lxc'

    def _strip_sudo(self, executable, cmd):
        # Get the command without sudo
        sudoless = cmd.rsplit(executable + ' -c ', 1)[1]
        # Get the quotes
        quotes = sudoless.partition('echo')[0]
        # Get the string between the quotes
        cmd = sudoless[len(quotes):-len(quotes + '?')]
        return cmd

    def host_command(self, cmd, do_become=False):
        if self._play_context.become and do_become:
            cmd = self._play_context.make_become_cmd(cmd)
        return super(Connection, self).exec_command(cmd, in_data=None, sudoable=True)

    def exec_command(self, cmd, in_data=None, executable='/bin/sh', sudoable=True):
        ''' run a command in the container '''

        cmd = '%s exec %s -- %s' % (self.get_container_connector(), self.get_container_id(), cmd)
        if self._play_context.become:
            cmd = self._play_context.make_become_cmd(cmd)

        return super(Connection, self).exec_command(cmd, in_data, True)

    def container_path(self, path):
        return self.get_container_id() + path

    @contextmanager
    def tempfile(self):
        code, stdout, stderr = self.host_command('mktemp')
        if code != 0:
            raise AnsibleError("failed to make temp file:\n%s\n%s" % (stdout, stderr))
        tmp = stdout.strip().split('\n')[-1]

        yield tmp

        code, stdout, stderr = self.host_command(' '.join(['rm', tmp]))
        if code != 0:
            raise AnsibleError("failed to remove temp file %s:\n%s\n%s" % (tmp, stdout, stderr))

    def put_file(self, in_path, out_path):
        ''' transfer a file from local to remote container '''
        with self.tempfile() as tmp:
            super(Connection, self).put_file(in_path, tmp)
            self.host_command(' '.join(['lxc', 'exec', self.get_container_id(), '--', 'mkdir', '-p', os.path.dirname(out_path)]), do_become=True)
            self.host_command(' '.join(['lxc', 'file', 'push', '--debug', tmp, self.container_path(out_path)]), do_become=True)

    def fetch_file(self, in_path, out_path):
        ''' fetch a file from remote to local '''
        with self.tempfile() as tmp:
            self.host_command(' '.join(['lxc', 'file', 'pull', self.container_path(in_path), tmp]), do_become=True)
            super(Connection, self).fetch_file(tmp, out_path)

    def close(self):
        ''' Close the connection, nothing to do for us '''
        super(Connection, self).close()
