#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/2/14 10:41 上午
# @Author  : Browser
# @File    : openvpn.py
# @Software: PyCharm
# @contact : browser_hot@163.com

import subprocess,re
from flask import jsonify
from lin import route_meta, group_required, login_required
from lin.exception import Success,ParameterException
from lin.redprint import Redprint
from app.libs.error_code import VirtualIPNotFound,OpenVPNNotFound

from app.models.openvpn import OpenVPNUser, OpenVPNLogInfo
from app.validators.forms import UserSearchForm, CreateUserForm, IPSearchForm, InfoSearchForm

from app.libs.shell import Remote_cmd

openvpn_api = Redprint('openvpn')
remote_server = Remote_cmd('192.168.149.150', '22222', 'root', 'epointP@ssw0rd')

# 创建用户
@openvpn_api.route('', methods=['POST'])
# @login_required
def create_user():
    form = CreateUserForm().validate_for_api()
    result = OpenVPNUser.new_user(form)
    # print('%s' % result)
    if result is True:
        command = ["/usr/local/bin/vpnuser", "add", form.username.data]
        command = ' '.join(str(d) for d in command)
        remote_server.onetime_shell(command)
        return Success(msg='用户创建成功')

    # if result is True:
    #     command = ["/usr/local/bin/vpnuser", "add", form.username.data]
    #     p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
    #     p.wait()
    #     if p.poll() == 0:
    #         print(p.communicate())
    #         return Success(msg='用户创建成功')
    #     else:
    #         raise ParameterException(msg="vpnuser创建失败")

# 查询单个用户
@openvpn_api.route('/<vid>', methods=['GET'])
# @login_required
def get_user(vid):
    user = OpenVPNUser.get_detail(vid)
    return jsonify(user)

# 查询所有用户
@openvpn_api.route('', methods=['GET'])
# @login_required
def get_users():
    users = OpenVPNUser.get_all()
    return jsonify(users)

# 根据username注销用户
@openvpn_api.route('', methods=['DELETE'])
@route_meta(auth='注销openvpn账号', module='用户')
# @group_required
def delete_openvpnuser():
    form = CreateUserForm().validate_for_api()
    result = OpenVPNUser.delete_user(form)
    if result is True:
        command = ["/usr/local/bin/vpnuser", "del", form.username.data]
        command = ' '.join(str(d) for d in command)
        remote_server.onetime_shell(command)
        return Success(msg='注销创建成功')

# 更新用户mac
@openvpn_api.route('/update', methods=['POST'])
# @login_required  # 只有在登入后后才可访问
def update_mac():
    form = IPSearchForm().validate_for_api()
    command = ["/usr/local/bin/update_user_mac.sh", form.openvpn_ip.data]
    command = ' '.join(str(d) for d in command)
    value = remote_server.onetime_shell(command)
    print('%s' % value)
    if re.findall(r'已更新', value):
        return Success(msg='MAC地址更新成功')
    else:
        raise VirtualIPNotFound

# 根据vid注销用户信息
@openvpn_api.route('/<vid>', methods=['DELETE'])
@route_meta(auth='注销用户', module='用户')  # 将这个视图函数注册到权限管理容器中；auth的名称为"注销用户"模块名为"用户"
# @group_required   # 只有在权限组授权后才可访问
def delete_user(vid):
    result = OpenVPNUser.remove_user(vid)
    return Success(msg='注销用户成功')

# 用户表查询
@openvpn_api.route('/search', methods=['GET'])
# @login_required
def search():
    form = UserSearchForm().validate_for_api()
    users = OpenVPNUser.search_by_user(form.openvpn_user_info.data)
    return jsonify(users)

# 根据用户查询IP
@openvpn_api.route('/searchip', methods=['GET'])
def get_user_ip():
    form = UserSearchForm().validate_for_api()
    command = ["/usr/local/bin/get_user_ip.sh",form.openvpn_user_info.data]
    command = ' '.join(str(d) for d in command)
    value = remote_server.onetime_shell(command)
    # print('%s' % value)
    # ip_pattern = r'(^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$)'
    # matching = re.findall(ip_pattern, value)
    if re.findall('未注册',value):
        return ParameterException(msg='未注册')
    else:
        # print('%s' % matching)
        return value

# 根据IP查询用户
@openvpn_api.route('/searchuser', methods=['GET'])
def get_ip_user():
    form = IPSearchForm().validate_for_api()
    command = ["/usr/local/bin/get_user_ip.sh",form.openvpn_ip.data]
    command = ' '.join(str(d) for d in command)
    value = remote_server.onetime_shell(command)
    if re.findall('没有', value):
        raise OpenVPNNotFound
    else:
        return value

# 绑定arp
@openvpn_api.route('/arpbinding', methods=['POST'])
# @login_required
def arp_binding():
    remote_server.onetime_shell("/bin/bash /usr/local/bin/add_arp.sh")
    return Success(msg="arp绑定成功")

# 查询所有历史信息
@openvpn_api.route('/info', methods=['GET'])
# @login_required
def get_info():
    info = OpenVPNLogInfo.get_all()
    return jsonify(info)

# 根据common_name查询历史信息
@openvpn_api.route('/infousersearch', methods=['GET'])
# @login_required
def search_user_info():
    form = InfoSearchForm().validate_for_api()
    common_name = OpenVPNLogInfo.search_user_info(form.common_name.data)
    return jsonify(common_name)

# 根据ip查询历史信息
@openvpn_api.route('/infoipsearch', methods=['GET'])
# @login_required
def search_ip_info():
    form = IPSearchForm().validate_for_api()
    ip = OpenVPNLogInfo.search_ip_info(form.openvpn_ip.data)
    return jsonify(ip)

# 查看当前已连接客户端数量
@openvpn_api.route('clientsconnected', methods=['GET'])
# @login_required
def get_clients_connected():
    pass

# 查询已连接客户端信息
@openvpn_api.route('clientslist', methods=['GET'])
# @login_required
def get_clientslist():
    pass

# 断开用户连接
@openvpn_api.route('closedclient', methods=['POST'])
# @login_required
def closed_client():
    pass

