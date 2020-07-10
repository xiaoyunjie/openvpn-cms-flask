#!/bin/bash
##Date:         2019-08-09
##Author:       Browser
##Description:  disconnect openvpn
##Version:      1.0

DB='openvpn'
DBADMIN='root'
PASSWD='Gepoint'
HOST='127.0.0.1'
#LOG='/var/log/openvpn/openvpn.log'
MYSQL='/usr/bin/mysql'

$MYSQL -u$DBADMIN -p$PASSWD -h$HOST -e "UPDATE log SET end_time=now(),bytes_received=$bytes_received,bytes_sent=$bytes_sent WHERE trusted_ip='$trusted_ip' and trusted_port='$trusted_port' and remote_ip='$ifconfig_pool_remote_ip' and remote_netmask='$ifconfig_pool_netmask' and common_name='$common_name'" $DB
