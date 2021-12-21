#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/6/16 4:34 下午
# @Author  : Browser
# @File    : socket-1.py
# @Software: PyCharm
# @contact : browser_hot@163.com

import os
import re
import sys
import socket

from datetime import datetime
from ipaddress import ip_address
from collections import deque


try:
    import GeoIP

    geoip1_available = True
except ImportError:
    geoip1_available = False

try:
    from geoip2 import database
    from geoip2.errors import AddressNotFoundError

    geoip2_available = True
except ImportError:
    geoip2_available = False


def info(*objs):
    print("INFO:", *objs, file=sys.stderr)


def warning(*objs):
    print("WARNING:", *objs, file=sys.stderr)


def debug(*objs):
    print("DEBUG:\n", *objs, file=sys.stderr)


def get_date(date_string, uts=False):
    if not uts:
        return datetime.strptime(date_string, "%a %b %d %H:%M:%S %Y")
    else:
        return datetime.fromtimestamp(float(date_string))


def get_str(s):
    if sys.version_info[0] == 2 and s is not None:
        return s.decode('ISO-8859-1')
    else:
        return s


class OpenvpnSocket(object):

    def __init__(self):
        geoip_data = os.path.join(os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + os.path.sep + "../.."),
                                  'GeoLite2-City.mmdb')
        self.geoip_version = None
        self.gi = None
        try:
            if geoip_data.endswith('.mmdb') and geoip2_available:
                self.gi = database.Reader(geoip_data)
                self.geoip_version = 2
            elif geoip_data.endswith('.dat') and geoip1_available:
                self.gi = GeoIP.open(geoip_data, GeoIP.GEOIP_STANDARD)
                self.geoip_version = 1
            else:
                warning('No compatible geoip1 or geoip2 data/libraries found.')
        except IOError:
            warning('No compatible geoip1 or geoip2 data/libraries found. IOError')


    def _socket_send(self, command):
        if sys.version_info[0] == 2:
            self.s.send(command)
        else:
            self.s.send(bytes(command, 'utf-8'))

    def _socket_recv(self, length):
        if sys.version_info[0] == 2:
            return self.s.recv(length)
        else:
            return self.s.recv(length).decode('utf-8')

    def _socket_connect(self, host, port):
        timeout = 3
        self.s = False
        try:
            self.s = socket.create_connection((host, port), timeout)
        except socket.timeout as e:
            print('str(e):\t\t', str(e))
            if self.s:
                self.s.shutdown(socket.SHUT_RDWR)
                self.s.close()

    def _socket_disconnect(self):
        self._socket_send('quit\n')
        self.s.shutdown(socket.SHUT_RDWR)
        self.s.close()

    def send_command(self, command):
        self._socket_send(command)
        data = ''
        while 1:
            socket_data = self._socket_recv(1024)
            socket_data = re.sub('>INFO(.)*\r\n', '', socket_data)
            data += socket_data
            if command == 'load-stats\n' and data != '':
                break
            elif data.endswith("\nEND\r\n"):
                break
        return data

    @staticmethod
    def parse_stats(data):
        line = re.sub('SUCCESS: ', '', data)
        parts = line.split(',')
        stats = parts[0]
        res = stats.split('=')
        nclients = res[1]
        return nclients

    def parse_status(self, data):
        gi = self.gi
        geoip_version = self.geoip_version
        client_section = False
        sessions = []

        for line in data.splitlines():
            parts = deque(line.split('\t'))
            if parts[0].startswith('END'):
                break
            if parts[0].startswith('TITLE') or \
                    parts[0].startswith('GLOBAL') or \
                    parts[0].startswith('TIME'):
                continue
            if parts[0] == 'HEADER':
                if parts[1] == 'CLIENT_LIST':
                    client_section = True
                if parts[1] == 'ROUTING_TABLE':
                    client_section = False
                continue

            if client_section:
                session = {}
                parts.popleft()
                common_name = parts.popleft()
                remote_str = parts.popleft()
                if remote_str.count(':') == 1:
                    remote, port = remote_str.split(':')
                elif '(' in remote_str:
                    remote, port = remote_str.split('(')
                    port = port[:-1]
                else:
                    remote = remote_str
                    port = None
                remote_ip = ip_address(remote)
                session['remote_ip'] = remote
                if port:
                    session['port'] = int(port)
                else:
                    session['port'] = ''
                if remote_ip.is_private:
                    session['location'] = 'RFC1918'
                else:
                    try:
                        if geoip_version == 1:
                            gir = gi.record_by_addr(str(remote_ip))
                            if gir is not None:
                                session['location'] = gir['country_code']
                                session['region'] = get_str(gir['region'])
                                session['city'] = get_str(gir['city'])
                                session['country'] = gir['country_name']
                                session['longitude'] = gir['longitude']
                                session['latitude'] = gir['latitude']
                        elif geoip_version == 2:
                            gir = gi.city(str(remote_ip))
                            session['location'] = gir.country.iso_code
                            session['region'] = gir.subdivisions.most_specific.iso_code
                            if not session['region']:
                                session['region'] = 'N/A'
                            session['city'] = gir.city.name
                            if not session['city']:
                                session['city'] = 'N/A'
                            session['country'] = gir.country.name
                            session['longitude'] = gir.location.longitude
                            session['latitude'] = gir.location.latitude
                    except AddressNotFoundError:
                        pass
                    except SystemError:
                        pass
                local_ipv4 = parts.popleft()
                if local_ipv4:
                    session['local_ip'] = local_ipv4
                else:
                    session['local_ip'] = ''
                # if version.major >= 2 and version.minor >= 4:
                local_ipv6 = parts.popleft()
                if local_ipv6:
                    session['local_ip'] = local_ipv6
                session['bytes_recv'] = int(parts.popleft())
                session['bytes_sent'] = int(parts.popleft())
                parts.popleft()
                session['connected_since'] = str(get_date(parts.popleft(), uts=True))
                username = parts.popleft()
                if username != 'UNDEF':
                    session['username'] = username
                else:
                    session['username'] = common_name
                # if version.major == 2 and version.minor >= 4:
                #     session['client_id'] = parts.popleft()
                #     session['peer_id'] = parts.popleft()
                # sessions[str(session['local_ip'])] = session
                sessions.append(session)
        # sessions = json.dumps(sessions)
        # print(session)
        # print(sessions)
        return sessions

    @staticmethod
    def parse_version(data):
        for line in data.splitlines():
            if line.startswith('OpenVPN'):
                # print(a["version"])
                # return line.replace('OpenVPN Version: ', '')
                return line

    def collect_data_version(self, host, port):
        self._socket_connect(host, port)
        ver = self.send_command('version\n')
        version = str(self.parse_version(ver))
        self._socket_disconnect()
        # print(version)
        return version

    def collect_data_stats(self, host, port):
        self._socket_connect(host, port)
        stats = self.send_command('load-stats\n')
        vpn_stats = str(self.parse_stats(stats))
        self._socket_disconnect()
        # print(vpn_stats)
        return vpn_stats

    def collect_data_sessions(self, host, port):
        self._socket_connect(host, port)
        status = self.send_command('status 3\n')
        vpn_sessions = self.parse_status(status)
        self._socket_disconnect()
        # print(vpn_sessions)
        return vpn_sessions

