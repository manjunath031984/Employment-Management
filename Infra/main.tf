resource "google_container_cluster" "employment_mgmt" {

  name     = var.cluster_name
  location = var.region

  network    = var.network
  subnetwork = var.subnetwork

  # Regional cluster
  node_locations = [
    "us-central1-a",
    "us-central1-b"
  ]

  remove_default_node_pool = true
  initial_node_count       = 1

  deletion_protection = false
}

resource "google_container_node_pool" "employment_mgmt_nodes" {

  name     = "employment-mgmt-node-pool"
  location = var.region
  cluster  = google_container_cluster.employment_mgmt.name

  node_locations = [
    "us-central1-a",
    "us-central1-b"
  ]

  node_count = var.node_count

  node_config {

    image_type = "UBUNTU_CONTAINERD"

    disk_size_gb = 50
    disk_type    = "pd-balanced"

    machine_type = "e2-standard-4"

    service_account = var.service_account

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    labels = {
      environment = "dev"
      application = "employment-management"
    }

    tags = [
      "employment-mgmt-gke"
    ]

    metadata = {
      disable-legacy-endpoints = "true"
    }
  }
}