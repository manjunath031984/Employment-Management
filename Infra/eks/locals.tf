locals {
  cluster_name = "employment-mgmt-gke"

  availability_zones = [
    "us-east-1a",
    "us-east-1b",
    "us-east-1c"
  ]

  # Select one Default VPC subnet from each requested AZ.
  subnet_ids_by_az = {
    for az in local.availability_zones :
    az => [
      for subnet_id, subnet in data.aws_subnet.default :
      subnet_id if subnet.availability_zone == az
    ]
  }

  eks_subnet_ids = flatten([
    for az in local.availability_zones : local.subnet_ids_by_az[az]
  ])

  # Standard AWS tags used across the infrastructure.
  common_tags = {
    Project     = "Employment-Management"
    Application = "employment-management"
    Environment = var.environment
    ManagedBy   = "Terraform"
    Terraform   = "true"
    Platform    = "EKS"
    Owner       = "CloudAIOps"
  }

  cluster_tags = merge(local.common_tags, {
    Name = local.cluster_name
  })

  node_tags = merge(local.common_tags, {
    Name      = "${local.cluster_name}-node"
    Component = "worker-node"
  })
}
