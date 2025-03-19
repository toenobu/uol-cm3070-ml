## Several resource with Aws Cli
Several resource can not be managed with terraform due to the circulation reference.
I pick up below.

- s3 bucket to store the tf state
- x dynamo table to lock the state.
  - dynamo table is not needed anymore, because I can use s3 bucket to lock the state.
  - https://zenn.dev/terraform_jp/articles/terraform-s3-state-lock

### log

```
  # s3 Bucket

programboy-cm3070-foobarfoobarfoobar
programboy-cm3070-foobarfoobarfoobartf

  # Not public access
programboy-cm3070-foobarfoobarfoobar
programboy-cm3070-foobarfoobarfoobartf

  # Tagging
programboy-cm3070-foobarfoobarfoobar
programboy-cm3070-foobarfoobarfoobartf

  # Encryption
programboy-cm3070-foobarfoobarfoobar
programboy-cm3070-foobarfoobarfoobartf

  # Versioning
programboy-cm3070-foobarfoobarfoobar
programboy-cm3070-foobarfoobarfoobartf
```


```
  # Dynamodb

programboy-cm3070-foobarfoobarfoobar
  --attribute-definitions AttributeName=LockID,AttributeType=S --table-name example-ecspresso-tfstate \
  --key-schema AttributeName=LockID,KeyType=HASH --provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1

  # Tagging
programboy-cm3070-foobarfoobarfoobar
  --table-name example-ecspresso-tfstate | jq -r '.Table.TableArn')

  aws dynamodb tag-resource --region us-east-1 --profile programboy \
  --resource-arn "${DY_ARN}" --tags 'Key=Product,Value=site' --tags 'Key=awscli,Value=true'
```
