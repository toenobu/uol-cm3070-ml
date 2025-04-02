.PHONY: start stop shell help

WS_NAME := uol-cm3070-ml

up:
	devpod up . $(WS_NAME) --ide zed

reset:
	devpod up . --reset --ide zed

down:
	devpod stop $(WS_NAME)
