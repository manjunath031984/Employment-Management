output "namespace" {
  value = kubernetes_namespace.employment_management.metadata[0].name
}

output "service_account_name" {
  value = kubernetes_service_account.employment_management.metadata[0].name
}
