.PHONY: start stop shell help

WS_NAME := uol-cm3070-ml

up:
	devpod up . $(WS_NAME) --ide zed --provider ssh-cm3070-ml

reset:
	devpod up . --reset --ide zed --provider ssh-cm3070-ml

down:
	devpod stop $(WS_NAME) --provider ssh-cm3070-ml
