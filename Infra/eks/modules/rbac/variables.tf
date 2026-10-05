variable "namespace" {
  type        = string
  description = "Application namespace."
}

variable "service_account_name" {
  type        = string
  description = "Application ServiceAccount name."
}

variable "environment" {
  type        = string
  description = "Environment label."
}
