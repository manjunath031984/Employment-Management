variable "cluster_name" {
  type        = string
  description = "EKS cluster name."
}

variable "kubernetes_version" {
  type        = string
  description = "Kubernetes version."
}

variable "vpc_id" {
  type        = string
  description = "Existing VPC ID."
}

variable "subnet_ids" {
  type        = list(string)
  description = "Subnets for the EKS control plane and managed node group."
}

variable "node_instance_types" {
  type        = list(string)
  description = "EC2 instance types for the managed node group."
}

variable "desired_nodes" {
  type        = number
  description = "Desired number of worker nodes."
}

variable "min_nodes" {
  type        = number
  description = "Minimum number of worker nodes."
}

variable "max_nodes" {
  type        = number
  description = "Maximum number of worker nodes."
}

variable "node_disk_size" {
  type        = number
  description = "Worker node root disk size in GiB."
}

variable "environment" {
  type        = string
  default     = "dev"
  description = "Environment label."
}

variable "cluster_tags" {
  type        = map(string)
  description = "Tags applied to EKS cluster resources."
}

variable "node_tags" {
  type        = map(string)
  description = "Tags applied to managed node group resources."
}
