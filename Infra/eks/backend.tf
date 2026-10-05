terraform {
  backend "s3" {
    bucket         = "REPLACE_WITH_YOUR_TFSTATE_BUCKET"
    key            = "employment-mgmt-eks/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "REPLACE_WITH_YOUR_TFSTATE_LOCK_TABLE"

    # Recommended with newer Terraform versions.
    # DynamoDB locking above is retained because you requested it.
    use_lockfile = true
  }
}
