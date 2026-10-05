variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "cluster_name" {
  description = "GKE cluster name"
  type        = string
  default     = "employment-mgmt-gke"
}

variable "network" {
  description = "VPC network"
  type        = string
  default     = "default"
}

variable "subnetwork" {
  description = "Subnet"
  type        = string
  default     = "default"
}

variable "service_account" {
  description = "GKE node service account"
  type        = string
}

variable "node_count" {
  description = "Number of nodes per zone"
  type        = number
  default     = 1
}