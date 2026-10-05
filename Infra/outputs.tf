output "cluster_name" {
  value = google_container_cluster.employment_mgmt.name
}

output "cluster_location" {
  value = google_container_cluster.employment_mgmt.location
}

output "cluster_endpoint" {
  value = google_container_cluster.employment_mgmt.endpoint
}

output "node_pool_name" {
  value = google_container_node_pool.employment_mgmt_nodes.name
}