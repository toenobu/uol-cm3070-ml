.PHONY: start stop shell help

# I use the same VM as I used for the example-sagemaker-serveless
VM_NAME := example-sagemaker-serveless

init:
	limactl start --name $(VM_NAME) docker-rootful.yaml
	docker context create lima-$(VM_NAME) --docker "host=unix:///Users/toenobu/.lima/$(VM_NAME)/sock/docker.sock"
	docker context use lima-$(VM_NAME)

start:
	limactl start $(VM_NAME)
	docker context use lima-$(VM_NAME)

login:
	limactl shell $(VM_NAME)

stop:
	limactl stop $(VM_NAME)

show-ssh:
	limactl show-ssh $(VM_NAME)

login-as-root:
	limactl shell $(VM_NAME) -- sudo su -
