#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/2/17 11:35 上午
# @Author  : Browser
# @File    : openvpn.py
# @Software: PyCharm
# @contact : browser_hot@163.com


from lin.exception import NotFound, ParameterException
from lin.interface import InfoCrud as Base
from sqlalchemy import Column, String, Integer, or_, DateTime, Float,  func
# from flask_migrate import Migrate

from app.libs.error_code import OpenVPNNotFound

##  新增用户入库
class OpenVPNUser(Base):
    __tablename__ = 'openvpn_user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(30), nullable=False)
    nickname = Column(String(30), nullable=False)
    summary = Column(String(1000))

    @classmethod
    def get_detail(cls, vid):
        User = cls.query.filter_by(id=vid, delete_time=None).first()
        if User is None:
            raise NotFound(msg='没有找到相关用户')
        return User

    @classmethod
    def get_all(cls):
        Users = cls.query.filter_by(delete_time=None).all()
        if not Users:
            raise NotFound(msg='没有找到相关用户')
        return Users

    @classmethod
    def search_by_user(cls, openvpn_user_info):
        Users = cls.query.filter(or_(OpenVPNUser.username.like('%' + openvpn_user_info + '%'),
                                     OpenVPNUser.nickname.like('%' + openvpn_user_info + '%'),
                                     OpenVPNUser.summary.like('%' + openvpn_user_info + '%')),
                                 OpenVPNUser.delete_time == None).all()
        if not Users:
            raise OpenVPNNotFound
        return Users

    @classmethod
    def new_user(cls, form):
        User = OpenVPNUser.query.filter_by(username=form.username.data, delete_time=None).first()
        if User is not None:
            raise ParameterException(msg='用户已存在')

        OpenVPNUser.create(
            username=form.username.data,
            nickname=form.nickname.data,
            summary=form.summary.data,
            commit=True
        )
        return True

    @classmethod
    def remove_user(cls, vid):
        User = cls.query.filter_by(id=vid, delete_time=None).first()
        if User is None:
            raise NotFound(msg='没有找到相关用户')
        # 删除用户，软删除
        User.hard_delete(commit=True)
        return True

    @classmethod
    def delete_user(cls,form):
        User = cls.query.filter_by(username=form.username.data, delete_time=None).first()
        if User is None:
            raise NotFound(msg='没有找到相关用户')
        User.hard_delete(commit=True)
        return True

## openvpn用户登入历史信息
class OpenVPNLogInfo(Base):
    __tablename__ = 'log'
    id = Column(Integer, primary_key=True, autoincrement=True)
    starting_time = Column(DateTime, server_default=func.current_timestamp(), nullable=False)
    end_time = Column(DateTime, nullable=True)
    trusted_ip = Column(String(32), nullable=False)
    trusted_port = Column(Integer, nullable=False)
    protocol = Column(String(32), nullable=False)
    remote_ip = Column(String(32), nullable=False)
    remote_netmask = Column(String(32), nullable=False)
    common_name = Column(String(50), nullable=False)
    bytes_received = Column(Float, server_default='0', nullable=False)
    bytes_sent = Column(Float, server_default='0', nullable=False)

    @classmethod
    def get_all(cls):
        Info = cls.query.filter_by(delete_time=None).all()
        if not Info:
            raise NotFound(msg='没有找到相关登入信息')
        return Info

    @classmethod
    def search_user_info(cls, user_info):
        Users_Info = cls.query.filter_by(common_name == user_info, delete_time == None).all()

        if not Users_Info:
            raise OpenVPNNotFound
        return Users_Info

    @classmethod
    def search_ip_info(cls,  ip_info):
        IP_Info = cls.query.filter_by(or_(trusted_ip == ip_info, remote_ip == ip_info), delete_time == None).all()

        if not IP_Info:
            raise OpenVPNNotFound
        return IP_Info
