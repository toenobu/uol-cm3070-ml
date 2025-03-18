.PHONY: start stop shell help

WS_NAME := uol-cm3070-ml

up:
	devpod up . $(WS_NAME) --ide zed

down:
	devpod stop $(WS_NAME)
