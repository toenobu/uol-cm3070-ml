.PHONY: start stop shell help

VENV_DIRECTORY = venv

VM_NAME := cm3070-ml-serveless

VERSION = $(shell git describe --tags)

REGION = us-east-1
programboy-cm3070-foobarfoobarfoobar
ACCOUNT = 195275638784
IMAGE = cm3070_ml

init:
	uv init

activate:
	echo "Try 'source .$(VENV_DIRECTORY)/bin/activate'"

deactivate:
	echo "Try 'deactivate'"

upgrade:
	uv sync --upgrade

run:
	AWS_PROFILE=$(PROFILE) AWS_REGION=$(REGION) uv run app/main.py

run-lambda:
	aws lambda invoke \
		--region $(REGION) \
		--profile $(PROFILE) \
		--function-name cm3070-ml-serverless-lambda \
		--cli-binary-format raw-in-base64-out \
		--payload '{}' \
		--output text \
		/dev/stdout

aws-sso-login:
	aws sso login \
		--profile $(PROFILE) \
		--sso-session sso

build-image:
	uv lock
	docker build -t $(VM_NAME):$(VERSION) .

login-image:
	docker run -it --rm --entrypoint "/bin/bash" $(VM_NAME):$(VERSION)
	# https://stackoverflow.com/questions/76561064/how-can-i-access-the-shell-of-the-aws-lambda-images-on-ecr

ecr-login:
	aws ecr get-login-password --region $(REGION) --profile $(PROFILE) | docker login --username AWS --password-stdin $(ACCOUNT).dkr.ecr.$(REGION).amazonaws.com

push-image:
	docker tag $(VM_NAME):$(VERSION) $(ACCOUNT).dkr.ecr.us-east-1.amazonaws.com/$(IMAGE):$(VERSION)
	docker push $(ACCOUNT).dkr.ecr.us-east-1.amazonaws.com/$(IMAGE):$(VERSION)
