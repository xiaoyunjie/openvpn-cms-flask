#all: build push
#
#build:
#	docker buildx build --platform linux/arm64,linux/amd64  -t registry.cn-hangzhou.aliyuncs.com/browser/openvpn-cms-flask:v1.2.0 -f Dockerfile .  --push
#
#.PHONY: all build

all: build push

build:
	docker build --pull --platform linux/amd64 -t registry.cn-hangzhou.aliyuncs.com/browser/openvpn-cms-flask:v1.2.8 .

push:
	docker push registry.cn-hangzhou.aliyuncs.com/browser/openvpn-cms-flask:v1.2.8

.PHONY: all build push
