variable "aws_region" {
  description = "AWS region for the EKS cluster."
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name used in AWS resource tags."
  type        = string
  default     = "dev"
}

variable "node_instance_types" {
  description = "EC2 instance types for the EKS managed node group."
  type        = list(string)
  default     = ["t3.micro"]
}

variable "desired_nodes" {
  description = "Desired number of worker nodes."
  type        = number
  default     = 3
}

variable "min_nodes" {
  description = "Minimum number of worker nodes."
  type        = number
  default     = 3
}

variable "max_nodes" {
  description = "Maximum number of worker nodes."
  type        = number
  default     = 3
}

variable "node_disk_size" {
  description = "Worker node root disk size in GiB."
  type        = number
  default     = 30
}
