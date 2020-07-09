#!/bin/bash
##Date:         2019-08-09
##Author:       Browser
##Description:	update user mac
##Version:      1.0

USER=$1
IPP='/etc/openvpn/ipp.txt'
CAT='/bin/cat'

if [[ $# < 1 ]];then 
    echo "Please Input VPN_USER!!"
else
    IP=$($CAT $IPP | grep -w "$USER" | awk -F, '{print $2}')
    if [[ $IP != '' ]];then
        MAC_ADDRESS=$($CAT /etc/arp-map | grep -w "$IP" | awk '{print $2}')
        sed -i "/$IP/d" /etc/arp-map
        /sbin/arp -d $IP &>/dev/null 
        #echo "==================<温馨提示>=================="
        echo "$IP 的当前MAC地址为"$MAC_ADDRESS"，已更新"
        #echo "=============================================="
    else
        #echo "==================<温馨提示>=================="
        echo "没有 $IP 相关信息，未更新"
        #echo "=============================================="
    fi
fi
