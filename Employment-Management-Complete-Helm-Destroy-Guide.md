# 31. Employment Management — Complete Destroy Guide

## Purpose

Complete cleanup guide for the Employment Management lab after the successful Helm/GKE deployment.

This destroys the Helm release, Kubernetes workload, PostgreSQL persistent data, namespace, global static IP, GKE cluster, and Artifact Registry repository.

**GitHub repository, Git branches, local source files, Helm files, documentation, and `rendered.yaml` are not deleted.**

---

## 31.1 Environment

| Item | Value |
|---|---|
| GCP Project | `gcp-dev-july-2026` |
| GKE Cluster | `k8s-postgres-lab` |
| GKE Location | `us-central1` |
| Kubernetes Namespace | `stateful-demo` |
| Helm Release | `employment-management` |
| Artifact Registry Repository | `employment-management` |
| Artifact Registry Location | `us-central1` |
| Global Static IP Resource | `cloudaiops-gateway-ip` |
| Global Static IP | `34.160.13.80` |
| Domain | `cloudaiops.site` |

---

## 31.2 Destroy Order

```text
Helm release
    ↓
Kubernetes workloads
    ↓
PostgreSQL PVC/data
    ↓
Kubernetes namespace
    ↓
Global static IP
    ↓
GKE cluster
    ↓
Artifact Registry repository
    ↓
Hostinger DNS
```

---

## 31.3 Step 1 — Check Helm Release

```bash
helm list -n stateful-demo
```

Expected before uninstall:

```text
employment-management   stateful-demo   2   deployed   employment-management-0.1.0   3.0.0
```

---

## 31.4 Step 2 — Uninstall Helm Release

```bash
helm uninstall employment-management   -n stateful-demo
```

Verify:

```bash
helm list -n stateful-demo
```

The `employment-management` release should no longer appear.

---

## 31.5 Step 3 — Verify Kubernetes Workloads

```bash
kubectl get all -n stateful-demo
```

Expected:

```text
No resources found in stateful-demo namespace.
```

Also check:

```bash
kubectl get gateway -n stateful-demo
kubectl get httproute -n stateful-demo
```

---

## 31.6 Step 4 — Check PostgreSQL PVC

Helm uninstall does not automatically remove StatefulSet PVCs.

```bash
kubectl get pvc -n stateful-demo
```

The PVC used in this deployment was:

```text
postgres-data-employment-management-postgres-0
```

It contained the PostgreSQL database data.

---

## 31.7 Step 5 — Delete PostgreSQL PVC

**WARNING:** This permanently deletes the PostgreSQL persistent data.

Only run this if the database data is no longer required.

```bash
kubectl delete pvc postgres-data-employment-management-postgres-0   -n stateful-demo
```

Verify:

```bash
kubectl get pvc -n stateful-demo
```

Expected:

```text
No resources found in stateful-demo namespace.
```

---

## 31.8 Step 6 — Delete Kubernetes Namespace

If `stateful-demo` is dedicated only to this lab:

```bash
kubectl delete namespace stateful-demo
```

Verify:

```bash
kubectl get namespace stateful-demo
```

Expected:

```text
Error from server (NotFound): namespaces "stateful-demo" not found
```

Do not delete the namespace if other workloads use it.

---

## 31.9 Step 7 — Check Global Static IP

The Gateway used:

```text
cloudaiops-gateway-ip
```

which allocated:

```text
34.160.13.80
```

Check:

```bash
gcloud compute addresses describe cloudaiops-gateway-ip   --global   --project=gcp-dev-july-2026
```

---

## 31.10 Step 8 — Delete Global Static IP

If the environment is completely being destroyed:

```bash
gcloud compute addresses delete cloudaiops-gateway-ip   --global   --project=gcp-dev-july-2026
```

Confirm:

```text
Y
```

Verify:

```bash
gcloud compute addresses list   --global   --project=gcp-dev-july-2026
```

`cloudaiops-gateway-ip` should no longer be listed.

---

## 31.11 Step 9 — Delete GKE Cluster

Cluster:

```text
k8s-postgres-lab
```

Location:

```text
us-central1
```

Delete:

```bash
gcloud container clusters delete k8s-postgres-lab   --location=us-central1   --project=gcp-dev-july-2026
```

Confirm:

```text
Y
```

This deletes the GKE cluster and its node pools.

---

## 31.12 Step 10 — Verify GKE Cluster Deletion

```bash
gcloud container clusters list   --project=gcp-dev-july-2026
```

`k8s-postgres-lab` should no longer appear.

---

## 31.13 Step 11 — Delete Artifact Registry Repository

Repository:

```text
employment-management
```

Location:

```text
us-central1
```

Application image that was stored there:

```text
us-central1-docker.pkg.dev/gcp-dev-july-2026/employment-management/employment-management:3.0.0
```

Delete the repository:

```bash
gcloud artifacts repositories delete employment-management   --location=us-central1   --project=gcp-dev-july-2026
```

Confirm:

```text
Y
```

This deletes the repository and its stored container images.

---

## 31.14 Step 12 — Verify Artifact Registry

```bash
gcloud artifacts repositories list   --location=us-central1   --project=gcp-dev-july-2026
```

`employment-management` should no longer appear.

---

## 31.15 Step 13 — Hostinger DNS Cleanup

The public DNS record used was:

```text
Type:    A
Name:    @
Content: 34.160.13.80
TTL:     300
```

This configured:

```text
cloudaiops.site
        ↓
34.160.13.80
```

If the environment is permanently shut down, remove this Hostinger record:

```text
A   @   34.160.13.80
```

If a `www` record was created:

```text
CNAME   www   cloudaiops.site
```

remove it as well if it is no longer needed.

---

## 31.16 Complete Destroy Command Sequence

```bash
# 1. Check Helm release
helm list -n stateful-demo

# 2. Uninstall Helm release
helm uninstall employment-management   -n stateful-demo

# 3. Verify Kubernetes workloads
kubectl get all -n stateful-demo

# 4. Check PostgreSQL PVC
kubectl get pvc -n stateful-demo

# 5. Delete PostgreSQL PVC - DESTRUCTIVE
kubectl delete pvc postgres-data-employment-management-postgres-0   -n stateful-demo

# 6. Verify PVC
kubectl get pvc -n stateful-demo

# 7. Delete namespace
kubectl delete namespace stateful-demo

# 8. Delete global static IP
gcloud compute addresses delete cloudaiops-gateway-ip   --global   --project=gcp-dev-july-2026

# 9. Verify static IP
gcloud compute addresses list   --global   --project=gcp-dev-july-2026

# 10. Delete GKE cluster
gcloud container clusters delete k8s-postgres-lab   --location=us-central1   --project=gcp-dev-july-2026

# 11. Verify GKE cluster
gcloud container clusters list   --project=gcp-dev-july-2026

# 12. Delete Artifact Registry repository
gcloud artifacts repositories delete employment-management   --location=us-central1   --project=gcp-dev-july-2026

# 13. Verify Artifact Registry
gcloud artifacts repositories list   --location=us-central1   --project=gcp-dev-july-2026
```

---

## 31.17 Resources Deleted

| Resource | Action |
|---|---|
| Helm release `employment-management` | Deleted |
| Application Deployment | Deleted |
| Application Service | Deleted |
| PostgreSQL StatefulSet | Deleted |
| PostgreSQL Service | Deleted |
| PostgreSQL PVC | Deleted if full reset |
| PostgreSQL data | Deleted if PVC deleted |
| PostgreSQL ConfigMap | Deleted |
| PostgreSQL Secret | Deleted |
| TLS Secret | Deleted |
| Gateway | Deleted |
| HTTPRoute | Deleted |
| `stateful-demo` namespace | Deleted |
| Global IP `cloudaiops-gateway-ip` | Deleted |
| IP `34.160.13.80` | Released |
| GKE cluster `k8s-postgres-lab` | Deleted |
| Artifact Registry `employment-management` | Deleted |
| Artifact image `3.0.0` | Deleted |
| GitHub repository | Preserved |
| Git branches | Preserved |
| Local project files | Preserved |
| Helm chart | Preserved |
| Documentation | Preserved |
| `rendered.yaml` | Preserved |

---

## 31.18 Final Verification Checklist

### Helm

```bash
helm list -n stateful-demo
```

No `employment-management` release should remain.

### Kubernetes

```bash
kubectl get namespace stateful-demo
```

The namespace should be absent if deleted.

### GKE

```bash
gcloud container clusters list   --project=gcp-dev-july-2026
```

`k8s-postgres-lab` should be absent.

### Static IP

```bash
gcloud compute addresses list   --global   --project=gcp-dev-july-2026
```

`cloudaiops-gateway-ip` should be absent.

### Artifact Registry

```bash
gcloud artifacts repositories list   --location=us-central1   --project=gcp-dev-july-2026
```

`employment-management` should be absent.

### Hostinger

Remove or update:

```text
A   @   34.160.13.80
```

if the environment is permanently shut down.

---

## 31.19 What Is NOT Deleted

The destroy commands do not delete:

```text
GitHub repository
feature/helm-chart branch
main branch
Local source code
Local Helm chart
Chart.yaml
values.yaml
templates/
rendered.yaml
Deployment documentation
```

These remain available for the next rebuild.

---

## 31.20 Rebuild Note

After this destroy process, a future rebuild will need to recreate:

1. GKE cluster
2. Gateway API configuration
3. Artifact Registry repository
4. Application image
5. Kubernetes namespace
6. PostgreSQL storage
7. Helm release
8. Global static IP
9. Gateway
10. HTTPRoute
11. TLS Secret
12. Hostinger DNS pointing to the new Gateway IP

If the old static IP was deleted, a future deployment may receive a different IP.

---

## 31.21 Final Destroy State

```text
Helm release             → DELETED
Kubernetes workload      → DELETED
PostgreSQL PVC/data      → DELETED
Namespace                → DELETED
Global static IP         → RELEASED
GKE cluster              → DELETED
Artifact Registry repo   → DELETED
Hostinger DNS            → REMOVED/UPDATED
Git repository           → PRESERVED
Git branches             → PRESERVED
Local project files      → PRESERVED
```

The GCP/GKE lab environment is fully cleaned up while the source code and Helm deployment artifacts remain available for the next rebuild.
