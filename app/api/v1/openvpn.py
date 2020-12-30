#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/2/14 10:41 上午
# @Author  : Browser
# @File    : openvpn.py
# @Software: PyCharm
# @contact : browser_hot@163.com

import math
import os
import re

from flask import jsonify, send_from_directory, make_response, request
from lin import route_meta, group_required, login_required
from lin.exception import Success, ParameterException, NotFound
from lin.redprint import Redprint
from sqlalchemy import text

from app.libs.shell import Remote_cmd, Cmd
from app.libs.utils import get_page_from_query, json_res, paginate
from app.models.openvpn import OpenVPNUser, OpenVPNLogInfo
from app.validators.forms import UserSearchForm, CreateUserForm, IPSearchForm, HistoryInfoForm
from app.libs.manager_info import OpenvpnSocket
from app import VPN_ADDRESS, VPN_PORT

openvpn_api = Redprint('openvpn')
# 远程shell脚本执行
# remote_server = Remote_cmd('192.168.149.150', '22222', 'root', 'epointP@ssw0rd')
remote_server = Cmd()

# openvpn后台manager信息抽取
manager_info = OpenvpnSocket()


# 创建用户
@openvpn_api.route('', methods=['POST'])
@route_meta(auth='创建openvpn用户', module='用户', mount=True)
@group_required
def create_user():
    form = CreateUserForm().validate_for_api()
    result = OpenVPNUser.new_user(form)
    if result is True:
        command = ["/usr/local/bin/vpnuser", "add", form.username.data]
        command = ' '.join(str(d) for d in command)
        remote_server.onetime_shell(command)
        return Success(msg='用户创建成功')


# 查询单个用户
@openvpn_api.route('/<vid>', methods=['GET'])
@login_required
def get_user(vid):
    user = OpenVPNUser.get_detail(vid)
    return jsonify(user)


# 查询所有用户
@openvpn_api.route('', methods=['GET'])
@login_required
def get_users():
    start, count = paginate()
    users = OpenVPNUser.get_all(start, count)
    total = OpenVPNUser.get_total_nums()
    total_page = math.ceil(total / count)
    page = get_page_from_query()
    return json_res(count=count, page=page, total=total, total_page=total_page, items=users)


# 根据username注销用户
@openvpn_api.route('/deluser', methods=['DELETE', 'POST'])
@route_meta(auth='注销openvpn账号', module='用户', mount=True)
@group_required
def delete_openvpnuser():
    form = CreateUserForm().validate_for_api()
    result = OpenVPNUser.delete_user(form)
    if result is True:
        command = ["/usr/local/bin/vpnuser", "del", form.username.data]
        command = ' '.join(str(d) for d in command)
        remote_server.onetime_shell(command)
        return Success(msg='注销成功')


# 更新用户mac
@openvpn_api.route('/update', methods=['POST'])
@login_required  # 只有在登入后后才可访问
def update_mac():
    form = UserSearchForm().validate_for_api()
    command = ["/usr/local/bin/update_macaddress.sh", form.openvpn_user_info.data]
    command = ' '.join(str(d) for d in command)
    value = remote_server.onetime_shell(command)
    if re.findall(r'已更新', value):
        return Success(msg='MAC address updated successfully')
    else:
        return NotFound(msg='No MAC information')


# 搜索用户信息
@openvpn_api.route('/userinfosearch', methods=['GET'])
@login_required
def search_user():
    form = HistoryInfoForm().validate_for_api()
    keyword = request.args.get('keyword', default=None, type=str)
    if keyword is None or '':
        raise ParameterException(msg='搜索关键字不可为空')
    start, count = paginate()
    res = OpenVPNUser.query.filter(OpenVPNUser.nickname.like(f"%{keyword}%"))
    if form.username.data:
        res = OpenVPNUser.query.filter(OpenVPNUser.username == form.username.data)
    if form.start.data and form.end.data:
        res = res.filter(OpenVPNUser._create_time.between(form.start.data, form.end.data))
    total = res.count()
    res = res.order_by(text('create_time desc')).offset(start).limit(count).all()
    total_page = math.ceil(total / count)
    page = get_page_from_query()
    if not res:
        res = []
    return json_res(page=page, count=count, total=total, items=res, total_page=total_page)


# 根据用户查询IP
@openvpn_api.route('/searchip', methods=['GET', 'POST'])
@login_required
def get_user_ip():
    form = UserSearchForm().validate_for_api()
    command = ["/usr/local/bin/get_user_ip.sh", form.openvpn_user_info.data]
    command = ' '.join(str(d) for d in command)
    value = remote_server.onetime_shell(command)
    if re.findall('未注册', value):
        return ParameterException(msg='未注册')
    elif re.findall('未登入', value):
        return NotFound(msg='Never login')
    else:
        return Success(msg=value)


# 根据IP查询用户
@openvpn_api.route('/searchuser', methods=['POST'])
def get_ip_user():
    form = IPSearchForm().validate_for_api()
    command = ["/usr/local/bin/get_user_ip.sh", form.openvpn_ip.data]
    command = ' '.join(str(d) for d in command)
    value = remote_server.onetime_shell(command)
    if re.findall('没有', value):
        raise ParameterException(msg='Unregistered')
    else:
        return Success(msg=value)


# 绑定arp
@openvpn_api.route('/arpbinding', methods=['POST'])
# @login_required
def arp_binding():
    remote_server.onetime_shell("/bin/bash /usr/local/bin/add_arp.sh")
    return Success(msg="arp绑定成功")


# 查询所有历史信息(分页展示)
@openvpn_api.route('/info', methods=['GET'])
@login_required
def get_info():
    start, count = paginate()
    info = OpenVPNLogInfo.get_all(start, count)
    total = OpenVPNLogInfo.get_total_nums()
    total_page = math.ceil(total / count)
    page = get_page_from_query()
    return json_res(count=count, page=page, total=total, total_page=total_page, items=info)


# 搜索历史信息
@openvpn_api.route('/infosearch', methods=['GET'])
@login_required
def search_info():
    form = HistoryInfoForm().validate_for_api()
    keyword = request.args.get('keyword', default=None, type=str)
    if keyword is None or '':
        raise ParameterException(msg='搜索关键字不可为空')
    start, count = paginate()
    # logs = Log.query.filter(Log.message.like(f'%{keyword}%'))
    # res = OpenVPNLogInfo.query.filter(OpenVPNLogInfo.common_name.like((f'%{keyword}%')))
    res = OpenVPNLogInfo.query.filter(OpenVPNLogInfo.remote_ip.like(f"%{keyword}%"))
    if form.username.data:
        res = OpenVPNLogInfo.query.filter(OpenVPNLogInfo.common_name == form.username.data)
    if form.start.data and form.end.data:
        res = res.filter(OpenVPNLogInfo.starting_time.between(form.start.data, form.end.data))
    total = res.count()
    res = res.order_by(text('starting_time desc')).offset(start).limit(count).all()
    total_page = math.ceil(total / count)
    page = get_page_from_query()
    if not res:
        res = []
    return json_res(page=page, count=count, total=total, items=res, total_page=total_page)


# 下载证书
@openvpn_api.route('/download', methods=['GET'])
# @login_required
def download_cert():
    form = UserSearchForm().validate_for_api()
    filename = form.openvpn_user_info.data + ".zip"
    directory = os.path.abspath('/opt/vpnuser/')
    # directory = os.path.abspath('/Users/xiaoyunjie/Downloads/CRT')
    # print("download_path = ", directory)
    if os.path.isdir(directory):
        response = make_response(send_from_directory(directory, filename, as_attachment=True))
        print("response: ", response)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET'
        response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
        response.headers["Content-Disposition"] = "attachment; filename={}".format(filename.encode().decode('latin-1'))
        print("response_headers: ", response.headers)
        if not response:
            return NotFound(msg='File does not exist')
        return response
    return NotFound(msg='Directory does not exist')


# openvpn版本信息
@openvpn_api.route('/openvpnversion', methods=['GET'])
@login_required
def get_openvpn_version():
    version = manager_info.collect_data_version(VPN_ADDRESS, VPN_PORT)
    # print(version)
    return json_res(name=version)


# 当前已连接客户端数量load-stats
@openvpn_api.route('/clientsconnected', methods=['GET'])
@login_required
def get_clients_connected():
    nclients = manager_info.collect_data_stats(VPN_ADDRESS, VPN_PORT)
    # print(nclients)
    return json_res(nclients=nclients)


# 查询已连接客户端详细信息status 3
@openvpn_api.route('/clientslist', methods=['GET'])
@login_required
def get_clientslist():
    vpn_session = manager_info.collect_data_sessions(VPN_ADDRESS, VPN_PORT)
    return json_res(items=vpn_session)


# 总访问量
@openvpn_api.route('/totalvisits', methods=['GET'])
@login_required
def get_totalvisits():
    totalnumber = OpenVPNLogInfo.get_total_nums()
    return jsonify(totalnumber)


# 总用户数
@openvpn_api.route('/totalusers', methods=['GET'])
@login_required
def get_totalusers():
    totalusers = OpenVPNUser.get_total_nums()
    return jsonify(totalusers)


# 断开用户连接
# @openvpn_api.route('/closedclient', methods=['POST'])
# @login_required
# def closed_client():
#     pass
