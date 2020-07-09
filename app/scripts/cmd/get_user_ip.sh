#!/bin/bash
##Date:         2019-08-09
##Author:       Browser
##Description:  get user ip
##Version:      1.0

IPP='/etc/openvpn/ipp.txt'
INPUT_1=$1
CAT='/bin/cat'
#ARP_MAP='/etc/arp-map'

if [[ $# < 1 ]];then 
    echo "Please Input VPN_USER!!"
else
    if [[ $INPUT_1 =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
	IP=$INPUT_1
	USERNAME=$($CAT $IPP | grep -w "$IP" | awk -F',' '{print $1}')
	if [[ $USERNAME != '' ]];then
	   # echo "==================<温馨提示>=================="
	    echo "$IP 的VPN用户名是: $USERNAME"
	   # echo "=============================================="
	else
	   # echo "==================<温馨提示>=================="
	    echo "没有 $IP 相关信息"
	   # echo "=============================================="
	fi
    else
	VPN_USER=$INPUT_1
	USERINFO=$($CAT $IPP | grep -w "$VPN_USER" | awk -F, '{print $1}')
	if [ -f /etc/openvpn/easy-rsa/3.0/pki/issued/$VPN_USER.crt ];then
	    if [ -z $USERINFO ];then
		echo "用户 $VPN_USER 未登入"
	    fi
	    VPN_ADDRESS=$(cat $IPP | grep -w $VPN_USER | awk -F',' '{print $2}')
	   # echo "==================<温馨提示>=================="
	    echo "$VPN_USER 的VPN地址是: $VPN_ADDRESS"
	   # echo "=============================================="
	else
	   # echo "==================<温馨提示>=================="
	    echo "用户 $VPN_USER 未注册"
	   # echo "=============================================="
	fi
    fi
fi
