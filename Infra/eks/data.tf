# Use the existing AWS Default VPC.
data "aws_vpc" "default" {
  default = true
}

# Get all subnets belonging to the Default VPC.
data "aws_subnets" "default_vpc" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# Read subnet details so we can select one subnet in each AZ.
data "aws_subnet" "default" {
  for_each = toset(data.aws_subnets.default_vpc.ids)
  id       = each.value
}
