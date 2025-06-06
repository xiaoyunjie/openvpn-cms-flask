FROM --platform=linux/amd64 registry.cn-hangzhou.aliyuncs.com/browser/python:3.8.19-2
LABEL maintainer="Browser <browser_hot@163.com>"

# 设置环境变量
# 防止 python 将 pyc 文件写入硬盘
ENV PYTHONDONTWRITEBYTECODE=1
# 防止 python 缓冲 (buffering) stdout 和 stderr, 以便更容易地进行容器日志记录
ENV PYTHONUNBUFFERED=1

WORKDIR /opt/openvpn-cms-flask

COPY . .

# vpn init script
RUN cp -r /opt/openvpn-cms-flask/bin/*  /usr/local/bin/  \
    && chmod a+x /usr/local/bin/* \
    && cp /opt/openvpn-cms-flask/app/scripts/cmd/* /usr/local/bin/ \
    && sed -i s/127.0.0.1/mysql/g /usr/local/bin/connect.sh \
    && sed -i s/127.0.0.1/mysql/g /usr/local/bin/disconnect.sh \
    && chmod 755 -R /usr/local/bin/

# python
RUN set -ex \
    && yum makecache \
    && yum install -y gcc GeoIP GeoIP-devel net-tools  \
    && pip3 install --no-cache-dir -r requirements.txt  -i https://pypi.tuna.tsinghua.edu.cn/simple \
    && sed -i s/localhost/mysql/g  /opt/openvpn-cms-flask/app/config/secure.py

# openvpn
RUN set -ex \
    && yum install -y epel-release \
    && yum install -y openvpn  easy-rsa  expect zip unzip net-tools telnet mysql netcat \
    && yum clean all


# arp script
#ADD cronfile /etc/cron.d/arp-cron

RUN set -ex \
    && rm -rf /etc/localtime \
    && ln -s /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

#    && chmod 0644 /etc/cron.d/arp-cron \
#    && touch /var/log/cron.log \
#    && env | grep -v "no_proxy" >> /etc/environment \

VOLUME ["/etc/openvpn"]
VOLUME ["/opt/vpnuser"]

# 暴露端口
EXPOSE 5000
EXPOSE 11940/udp

CMD ["vpn_run"]

