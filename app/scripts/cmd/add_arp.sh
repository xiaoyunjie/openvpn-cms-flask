#!/bin/bash
##Date:         2019-08-09
##Author:       Browser
##Description:  Binding MAC address
##Version:      1.0

## arp静态绑定，PERM指永久生效flag 0x6

CAT='/bin/cat'
ARP_MAP='/etc/arp-map'
CLIENT_IP=`/sbin/arp -an | grep tap0 | grep -v PERM | grep -v incomplete | awk '{print $2 }' | sed 's/[\(\)]//g'`
ARP=`cat /proc/net/arp | grep tap0 | grep "0x6" | awk '{print $1}'`


if [[ $ARP != '' ]];then
    for i in $CLIENT_IP
    do
	MATCH=$($CAT /proc/net/arp | grep tap0 | grep "0x6" | grep -w $i | awk '{print $1}')
        if [[ $MATCH != '' ]];then
	    continue
        else
	    /sbin/arp -an | grep tap0 | grep -v PERM | grep -v incomplete | awk '{print ($2 " " $4)}' | sed 's/[\(\)]//g' | grep -w $i >> $ARP_MAP
        fi
    done
else
    /sbin/arp -an | grep tap0 | grep -v PERM | grep -v incomplete | awk '{print ($2 " " $4)}' | sed 's/[\(\)]//g' >> $ARP_MAP
fi

/sbin/arp -f $ARP_MAP

