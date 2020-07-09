
### 一、需求
使用`openvpn`开源系统构建了一整套满足vpn需求的产品。一开始仅仅搭建了`openvpn`的裸服务端，通过简单的创建、删除和解绑脚本来维护系统。
**痛点：**
- 使用人员需要一定的Linux基础
- 脚本操作容易出错，导致证书丢失
- 操作交互不友好，体验差
- 登入信息无法查询
- 解绑MAC、注销用户不方便
- 没有开放的API调用
- 流程不优，人力资源浪费

`需要一套针对openvpn的内容管理系统，操作简单、维护方便、交互体验好、有日志查询、权限管控、开放API等功能，同时提供插件扩展。`

### 二、选型设计
经过筛选，选择前后端分离，全部通过API交互，方便后续前后端系统的重构。
**前端选择：**`VUE`
**后端选择：**`FLASK`
**数据库：**`Mysql`
**语言环境：**`Python`

基于开源框架Lin-cms二次开发，快速实现业务系统上线。


### 三、安装部署
#### openvpn
yum install 

#### CentOS 7
- python 3.6+
- mysql 5.6+
- openvpn 2.4.7+

##### 数据库
`curl -O http://repo.mysql.com/mysql-community-release-el7-5.noarch.rpm`

`rpm -ivh mysql-community-release-el7-5.noarch.rpm`

`yum install -y epel-release   mysql-community-server`

```sql
mysql -u root -p
create user 'root'@'localhost' identified by 'Gepoint';
create database openvpn;
grant all on *.* to 'root'@'%';
flush privileges;
exit
```

##### python36
`yum install -y gcc GeoIP GeoIP-devel python36  python36-setuptools  python36-devel`

`easy_install-3.6 pip`

##### openvpn-cms-flask
`git clone https://github.com/xiaoyunjie/openvpn-cms-flask.git`

`cd openvpn-cms-flask && python3.6 -m venv venv`

```bash
## 指定pip源，加速下载
mkdir -p  /root/.pip/
cat >  /root/.pip/pip.conf   <<EOF
[global]
trusted-host=mirrors.aliyun.com
index-url=http://mirrors.aliyun.com/pypi/simple/
EOF
```

`source venv/bin/activate && pip3 install --upgrade pip && pip3 install -r requirements.txt`

`python3.6 start.py`

http://localhost:5000