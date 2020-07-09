#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/2/25 10:07 上午
# @Author  : Browser
# @File    : shell.py
# @Software: PyCharm
# @contact : browser_hot@163.com

import subprocess
import paramiko


class Cmd(object):

    def onetime_shell(self, cmd):
        cmd = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        cmd = cmd.communicate()
        cmd = cmd[0].decode().rstrip()
        return cmd
    # def realtime_shell(self,cmd):
    #     cmd = subprocess.call(cmd, shell=True)
    #     return cmd


class Remote_cmd(object):

    def __init__(self, IP, Port, User, Password):
    # def __init__(self,PrivateKey,IP,Port,User):
        # self.private_key = paramiko.RSAKey.from_private_key_file(PrivateKey)
        self.ssh = paramiko.SSHClient()
        self.set_missing_host_key_policy = self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # self.connect = self.ssh.connect(hostname=IP, port=Port, username=User,pkey=self.private_key)
        self.connect = self.ssh.connect(hostname=IP, port=Port, username=User, password=Password, timeout=10)

    def onetime_shell(self, cmd, notice=False):
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        result = stdout.read().decode('utf-8').rstrip()
        if notice:
           self.ssh.close()
        return result

    # def realtime_shell(self,cmd,notice=False):
    #     try:
    #        stdin, stdout, stderr = self.ssh.exec_command(cmd)
    #        for line in stdout:
    #            print(line.strip("\n"))
    #        for error in stderr:
    #            print(error.strip("\n"))
    #        if notice:
    #           self.ssh.close()
    #     except Exception as e:
    #        print("execute command %s error, error message is %s" % (cmd, e))
    #        return ""