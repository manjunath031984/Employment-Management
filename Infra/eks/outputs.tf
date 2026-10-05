output "cluster_name" {
  value       = module.eks.cluster_name
  description = "EKS cluster name."
}

output "cluster_endpoint" {
  value       = module.eks.cluster_endpoint
  description = "EKS API endpoint."
}

output "cluster_region" {
  value       = var.aws_region
  description = "AWS region."
}

output "default_vpc_id" {
  value       = data.aws_vpc.default.id
  description = "Existing Default VPC ID."
}

output "eks_subnet_ids" {
  value       = local.eks_subnet_ids
  description = "Default VPC subnet IDs used by EKS."
}

output "node_group_arn" {
  value       = try(module.eks.eks_managed_node_groups["default"].node_group_arn, null)
  description = "EKS managed node group ARN."
}
