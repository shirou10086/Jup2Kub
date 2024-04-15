# Update and upgrade the system
sudo apt update
sudo apt upgrade -y

# Install Docker
sudo apt install -y docker.io

# Configure Docker to use systemd as the cgroup driver
cat <<EOF | sudo tee /etc/docker/daemon.json
{
  "exec-opts": ["native.cgroupdriver=systemd"],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m"
  },
  "storage-driver": "overlay2"
}
EOF

# turn off firewalls 
sudo iptables -F && sudo iptables -t nat -F && sudo iptables -t mangle -F && sudo iptables -X
sudo swapoff -a

# Enable and restart Docker
sudo systemctl enable docker
sudo systemctl daemon-reload
sudo systemctl restart docker

# Install dependencies for Kubernetes
sudo apt-get install -y apt-transport-https ca-certificates curl

# Add the Kubernetes signing key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.29/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg

# This overwrites any existing configuration in /etc/apt/sources.list.d/kubernetes.list
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.29/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list

# Update apt package index with the new repository and install Kubernetes components
sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl

# Install pip as well for later usage of Jup2Kub
sudo apt install python3-pip
