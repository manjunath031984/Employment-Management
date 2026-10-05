resource "aws_s3_bucket" "employment_management_state" {
  bucket = "employment-management-tfstate"

  lifecycle {
    prevent_destroy = false
  }

  tags = {
    Name        = "employment-management-tfstate"
    Project     = "Employment-Management"
    Application = "Employment-Management-App"
    Environment = "dev"
    ManagedBy   = "Terraform"
    Purpose     = "Terraform-State"
  }
}

resource "aws_s3_bucket_versioning" "employment_management_state" {
  bucket = aws_s3_bucket.employment_management_state.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "employment_management_state" {
  bucket = aws_s3_bucket.employment_management_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "employment_management_state" {
  bucket = aws_s3_bucket.employment_management_state.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_dynamodb_table" "employment_management_lock" {
  name         = "employment-management-tflock"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    Name        = "employment-management-tflock"
    Project     = "Employment-Management"
    Application = "Employment-Management-App"
    Environment = "dev"
    ManagedBy   = "Terraform"
    Purpose     = "Terraform-State-Locking"
  }
}