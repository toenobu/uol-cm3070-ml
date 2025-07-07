.PHONY: start stop shell help run build test clean tidy fmt

WS_NAME := uol-cm3070-ml
USER := $(shell whoami)
LIMA_PORT := $(shell limactl ls -f '{{.Name}},{{.SSHLocalPort}}' | grep example-sagemaker-serveless | cut -d',' -f2)

add-provider:
	echo "Check config with limactl show-ssh"; \
	devpod provider add ssh --name ssh-cm3070-ml \
		-o HOST=$(USER)@127.0.0.1 \
		-o 'EXTRA_FLAGS=-o IdentityFile="/Users/$(USER)/.lima/_config/user" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o NoHostAuthenticationForLocalhost=yes -o GSSAPIAuthentication=no -o PreferredAuthentications=publickey -o Compression=no -o BatchMode=yes -o IdentitiesOnly=yes -o Ciphers="^aes128-gcm@openssh.com,aes256-gcm@openssh.com" -o User=toenobu -o ControlMaster=auto -o ControlPath="/Users/toenobu/.lima/example-sagemaker-serveless/ssh.sock" -o ControlPersist=yes -o Hostname=127.0.0.1 -o Port=$(LIMA_PORT)'

up:
	devpod up . $(WS_NAME) --ide zed --provider ssh-cm3070-ml --debug

reset:
	devpod up . --reset --ide zed --provider ssh-cm3070-ml

down:
	devpod stop $(WS_NAME) --provider ssh-cm3070-ml
