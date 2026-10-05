output "cluster_name" {
  value = module.eks.cluster_name
}

output "cluster_endpoint" {
  value     = module.eks.cluster_endpoint
  sensitive = true
}

output "cluster_certificate_authority_data" {
  value     = module.eks.cluster_certificate_authority_data
  sensitive = true
}

output "cluster_arn" {
  value = module.eks.cluster_arn
}

output "node_group_arns" {
  value = module.eks.eks_managed_node_groups[*].node_group_arn
}
