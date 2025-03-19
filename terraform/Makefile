.PHONY: aws-sso-login

# Variables
REGION := us-east-1
programboy-cm3070-foobarfoobarfoobar

aws-sso-login:
	aws sso login --sso-session sso --profile $(PROFILE)

start-notebook:
	aws sagemaker start-notebook-instance \
		--region $(REGION) \
		--profile $(PROFILE) \
		--notebook-instance-name my-notebook-instance

stop-notebook:
	aws sagemaker stop-notebook-instance \
		--region $(REGION) \
		--profile $(PROFILE) \
		--notebook-instance-name my-notebook-instance

edit-secret:
	sops edit secret.yaml --aws-profile $(PROFILE)
	# export SOPS_KMS_ARN="" you need to set this variable for the first time

show-service-quotas:
	aws service-quotas list-services \
		--region $(REGION) \
		--profile $(PROFILE)
