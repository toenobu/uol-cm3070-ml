# https://aws.amazon.com/ec2/instance-types/ go to accelerated compute section.
# https://docs.aws.amazon.com/sagemaker/latest/dg/notebooks-available-instance-types.html
# https://aws.amazon.com/sagemaker-ai/pricing/

# I have to be allowed to use "ml.g4dn.xlarge" instance
# https://us-east-1.console.aws.amazon.com/servicequotas/home/services/sagemaker/quotas

# ml.g4dn.xlarge for notebook instance usage 0 -> 2
# https://us-east-1.console.aws.amazon.com/servicequotas/home/services/sagemaker/quotas/L-D8B97089
resource "aws_servicequotas_service_quota" "notebook_instance_usage" {
  quota_code   = "L-D8B97089"
  service_code = "sagemaker"
  value        = 2
}

# ml.g4dn.xlarge for training job usage 0 -> 1
# https://us-east-1.console.aws.amazon.com/servicequotas/home/services/sagemaker/quotas/L-3F53BF0F
resource "aws_servicequotas_service_quota" "training_job_usage" {
  quota_code   = "L-3F53BF0F"
  service_code = "sagemaker"
  value        = 1
}
