output "namespace" {
  value = kubernetes_namespace_v1.employment_management.metadata[0].name
}

output "service_account_name" {
  value = kubernetes_service_account_v1.employment_management.metadata[0].name
}
