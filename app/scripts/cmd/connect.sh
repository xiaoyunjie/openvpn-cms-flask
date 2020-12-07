#!/bin/bash
##Date:         2019-08-09
##Author:       Browser
##Description:  connect openvpn
##Version:      1.0


DB='openvpn'
DBADMIN='root'
PASSWD='openvpn'
HOST='127.0.0.1'
MYSQL='/usr/bin/mysql'

$MYSQL -u $DBADMIN -p$PASSWD -h$HOST -e "INSERT into log (starting_time,trusted_ip,trusted_port,protocol,remote_ip,remote_netmask,common_name)values(now(),'$trusted_ip','$trusted_port','$proto_1','$ifconfig_pool_remote_ip','$ifconfig_pool_netmask','$common_name')" $DB
