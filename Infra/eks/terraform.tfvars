aws_region  = "us-east-1"
environment = "dev"

# Change this if your AWS account has a different eligible instance type.
node_instance_types = ["t3.medium"]

desired_nodes = 3
min_nodes     = 3
max_nodes     = 3

node_disk_size = 30
