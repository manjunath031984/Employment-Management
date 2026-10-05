# Employment Management - AWS EKS Terraform

Creates an AWS EKS cluster in `us-east-1` using the existing AWS **Default VPC**.

## Architecture

- EKS cluster: `employment-mgmt-gke`
- Region: `us-east-1`
- Availability Zones:
  - `us-east-1a`
  - `us-east-1b`
  - `us-east-1c`
- Existing Default VPC is used.
- 3 EKS managed worker nodes.
- Kubernetes RBAC enabled for the application namespace.
- Application ServiceAccount created.
- Terraform state stored in S3.
- State locking configured with DynamoDB and S3 lockfile support.

## Important backend prerequisite

Create the S3 state bucket and DynamoDB lock table before running `terraform init`.

Then replace these values in `backend.tf`:

```text
REPLACE_WITH_YOUR_TFSTATE_BUCKET
REPLACE_WITH_YOUR_TFSTATE_LOCK_TABLE
```

The backend block cannot use variables from `terraform.tfvars`.

## Commands

```bash
terraform fmt -recursive
terraform init
terraform validate
terraform plan
terraform apply
```

After creation:

```bash
aws eks update-kubeconfig   --region us-east-1   --name employment-mgmt-gke

kubectl get nodes
kubectl get namespaces
```

## Important

The worker nodes use the EKS-optimized Amazon Linux 2023 AMI.

If Ubuntu 26.04 is a hard requirement, do not simply put an Ubuntu AMI ID into this managed-node-group configuration. That requires a different/custom node provisioning design.


## Local module structure

This configuration intentionally uses local Terraform modules:

```text
Infra/eks/
├── backend.tf
├── data.tf
├── eks.tf
├── kubernetes-provider.tf
├── locals.tf
├── outputs.tf
├── provider.tf
├── rbac.tf
├── terraform.tfvars
├── variables.tf
├── versions.tf
└── modules/
    ├── eks/
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    └── rbac/
        ├── main.tf
        ├── variables.tf
        └── outputs.tf
```

The `modules/eks` module wraps `terraform-aws-modules/eks/aws`.
The `modules/rbac` module creates the application namespace, ServiceAccount,
Role and RoleBinding.

The VPC is **not** created by Terraform here; the configuration reads the
existing AWS Default VPC and its subnets.
