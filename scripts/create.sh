# !/bin/bash

# Disable memory paging and swapping
sudo swapoff -a

# # Set vm.max_map_count to recommended value
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf

# Reload kernel parameters
sudo sysctl -p

sudo mkdir -p /usr/share/opensearch/data

docker-compose -f "<your_host_server_path>"/opensearch/scripts/docker-compose.yml up -d

docker run -d --network="host" --name dashboard opensearchproject/opensearch-dashboards:latest

