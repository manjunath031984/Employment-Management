module "rbac" {
  source = "./modules/rbac"

  namespace           = "employment-management"
  service_account_name = "employment-management-sa"
  environment         = var.environment

  depends_on = [module.eks]
}
