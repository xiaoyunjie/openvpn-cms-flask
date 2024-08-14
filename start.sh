#!/bin/bash

echo -e "\033[31m 正在配置脚本 \033[0m"
mkdir -p /opt/script
cat << EOF > /opt/script/start_cms.sh
#!/bin/bash

ps aux | grep -v grep | egrep 'starter'

if [ \$? -ne 0 ]; then
  echo -e "\033[31m 不存在openvpn-cms进程，正常启动 \033[0m"
else
  echo -e "\033[31m 检测到openvpn-cms进程未退出，结束中 \033[0m"
  ps aux | egrep 'starter' | grep -v grep | awk '{ print \$2 }' | xargs kill -9
fi

#source /opt/openvpn-cms-flask/venv/bin/activate

source /root/.bashrc
conda activate openvpn-cms-flask

cd /opt/openvpn-cms-flask && python starter.py >>/var/log/openvpn-cms-flask.log   2>&1  &

exit 0
EOF

sleep 1s
cat << EOF > /opt/script/stop_cms.sh
#!/bin/bash

ps aux | egrep 'starter' | grep -v grep | awk '{ print \$2 }' | xargs kill -9

exit 0
EOF


sleep 1s
chmod +x /opt/script/start_cms.sh
chmod +x /opt/script/stop_cms.sh

echo -e "\033[31m 正在写入开机自启 \033[0m"
if grep -q '/bin/bash /opt/script/start_cms.sh' /etc/rc.local; then
        echo -e "\033[31m 自启脚本已经存在 \033[0m"
else
        chmod +x /etc/rc.local
        echo "/bin/bash /opt/script/start_cms.sh" >> /etc/rc.local
fi

exit 0
