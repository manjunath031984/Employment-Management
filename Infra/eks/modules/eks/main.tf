module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 21.0"

  name               = var.cluster_name
  kubernetes_version = var.kubernetes_version

  vpc_id     = var.vpc_id
  subnet_ids = var.subnet_ids

  endpoint_public_access = true
  enable_irsa            = true

  enable_cluster_creator_admin_permissions = true

  tags = var.cluster_tags

  eks_managed_node_groups = {
    default = {
      name = "${var.cluster_name}-ng"

      instance_types = var.node_instance_types

      min_size     = var.min_nodes
      max_size     = var.max_nodes
      desired_size = var.desired_nodes

      disk_size = var.node_disk_size
      subnet_ids = var.subnet_ids

      # EKS managed-node-group AMI.
      # This is intentionally not using the previously discussed EC2 AMI ID.
      ami_type = "AL2023_x86_64_STANDARD"

      labels = {
        environment = var.environment
        workload    = "employment-management"
      }

      tags = var.node_tags
    }
  }

  access_entries = {}
}
