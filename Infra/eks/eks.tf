module "eks" {
  source = "./modules/eks"

  cluster_name       = local.cluster_name
  kubernetes_version = "1.33"

  vpc_id     = data.aws_vpc.default.id
  subnet_ids = local.eks_subnet_ids

  node_instance_types = var.node_instance_types
  desired_nodes       = var.desired_nodes
  min_nodes           = var.min_nodes
  max_nodes           = var.max_nodes
  node_disk_size      = var.node_disk_size

  cluster_tags = local.cluster_tags
  node_tags    = local.node_tags
}
