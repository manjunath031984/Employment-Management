provider "aws" {
  region = var.aws_region

  # These tags are automatically added to supported AWS resources
  # created through this provider. Resource-specific Name/Component
  # tags are added explicitly where needed.
  default_tags {
    tags = local.common_tags
  }
}
