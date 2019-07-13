#!/usr/bin/python3.5
# -*- coding: utf-8 -*-
#
#  transfer.py
#
#  Copyright 2019 mbrunet <mbrunet@siamarco>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#
from os import path
from paramiko import SSHClient, AutoAddPolicy, RSAKey, SSHException, Transport
import socket


class Transfer:
    server = ""
    username = ""
    password = ""

    def __init__(self):
        self.sshpath = path.expanduser(path.join("~", ".ssh", "known_hosts"))

    def send(self, localpath, remotepath):
        ssh = SSHClient()
        ssh.load_host_keys(self.sshpath)
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        if self.password != "":
            ssh.connect(self.server, username=self.username, password=self.password)
        else:
            k = RSAKey.from_private_key_file(path.expanduser(path.join("~", ".ssh", "id_rsa")))
            ssh.connect(self.server, port=22, username=self.username, pkey=k)
        sftp = ssh.open_sftp()
        sftp.put(localpath, remotepath)
        sftp.close()
        ssh.close()

    def get(self, remotepath, localpath):
        ssh = SSHClient()
        ssh.load_host_keys(self.sshpath)
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(self.server, username=self.username, password=self.password)
        sftp = ssh.open_sftp()
        sftp.get(remotepath, localpath)
        sftp.close()
        ssh.close()

    def checkconnection(self):
        try:
            ssh = SSHClient()
            ssh.load_host_keys(self.sshpath)
            ssh.set_missing_host_key_policy(AutoAddPolicy())
            if self.password != "":
                ssh.connect(self.server, username=self.username, password=self.password)
            else:
                k = RSAKey.from_private_key_file(path.expanduser(path.join("~", ".ssh", "id_rsa")))
                ssh.connect(self.server, port=22, username=self.username, pkey=k,
                            timeout=10, banner_timeout=5, auth_timeout=5)
            ssh.close()
            return True
        except (SSHException, socket.error) as se:
            print(se)
            ssh.close()


# Transfer()
# tr.server = "10.121.255.3"
# tr.username = "root"
# tr.password = "temporale"
# tr.send("/home/mbrunet/tmp/backup1.tar.gz", path.join("/tmp/", "backup1.tar.gz"))
# tr.get(path.join("/tmp/", "backup1.tar.gz"), "/home/mbrunet/backup1.tar.gz")
