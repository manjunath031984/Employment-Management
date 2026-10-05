resource "kubernetes_namespace_v1" "employment_management" {
  metadata {
    name = var.namespace
    labels = {
      app         = "employment-management"
      environment = var.environment
      managed-by  = "terraform"
    }
  }
}

resource "kubernetes_service_account_v1" "employment_management" {
  metadata {
    name      = var.service_account_name
    namespace = kubernetes_namespace_v1.employment_management.metadata[0].name
    labels = {
      app        = "employment-management"
      managed-by = "terraform"
    }
  }
}

resource "kubernetes_role_v1" "employment_management_read" {
  metadata {
    name      = "employment-management-read"
    namespace = kubernetes_namespace_v1.employment_management.metadata[0].name
  }

  rule {
    api_groups = [""]
    resources  = ["pods", "services", "configmaps", "secrets"]
    verbs      = ["get", "list", "watch"]
  }

  rule {
    api_groups = ["apps"]
    resources  = ["deployments", "replicasets"]
    verbs      = ["get", "list", "watch"]
  }
}

resource "kubernetes_role_binding_v1" "employment_management_read" {
  metadata {
    name      = "employment-management-read"
    namespace = kubernetes_namespace_v1.employment_management.metadata[0].name
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "Role"
    name      = kubernetes_role_v1.employment_management_read.metadata[0].name
  }

  subject {
    kind      = "ServiceAccount"
    name      = kubernetes_service_account_v1.employment_management.metadata[0].name
    namespace = kubernetes_namespace_v1.employment_management.metadata[0].name
  }
}
