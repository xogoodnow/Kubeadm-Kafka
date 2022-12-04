#Add the following modules to k8s.conf file
cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
overlay
br_netfilter
EOF

#Enable the modules on the kerne;
sudo modprobe overlay
sudo modprobe br_netfilter


# sysctl params required by setup, params persist across reboots
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
EOF



# sysctl params required by setup, params persist across reboots
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
EOF

# Apply sysctl params without reboot
sudo sysctl --system

#Disable Swapp and make it permanent using a ron job
sudo swapoff -a
(crontab -l 2>/dev/null; echo "@reboot /sbin/swapoff -a") | crontab - || true


#Add the following modules to crio.conf file
cat <<EOF | sudo tee /etc/modules-load.d/crio.conf
overlay
br_netfilter
EOF

# Set up required sysctl params, these persist across reboots.
cat <<EOF | sudo tee /etc/sysctl.d/99-kubernetes-cri.conf
net.bridge.bridge-nf-call-iptables  = 1
net.ipv4.ip_forward                 = 1
net.bridge.bridge-nf-call-ip6tables = 1
EOF



#Enable the modules in the kerne;
sudo modprobe overlay
sudo modprobe br_netfilter

#Enable the following modules in 99-kubernetes-cri.conf file
cat <<EOF | sudo tee /etc/sysctl.d/99-kubernetes-cri.conf
net.bridge.bridge-nf-call-iptables  = 1
net.ipv4.ip_forward                 = 1
net.bridge.bridge-nf-call-ip6tables = 1
EOF

#Reload system modules
sudo sysctl --system

#Set the following environment variables
OS="xUbuntu_22.04"
VERSION="1.25"

#Add the repo to install crio
cat <<EOF | sudo tee /etc/apt/sources.list.d/devel:kubic:libcontainers:stable.list
deb https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/$OS/ /
EOF

#Add the repo to install crio

cat <<EOF | sudo tee /etc/apt/sources.list.d/devel:kubic:libcontainers:stable:cri-o:$VERSION.list
deb http://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable:/cri-o:/$VERSION/$OS/ /
EOF

#Add the keys to be able to get the packages
curl -L https://download.opensuse.org/repositories/devel:kubic:libcontainers:stable:cri-o:$VERSION/$OS/Release.key | sudo apt-key --keyring /etc/apt/trusted.gpg.d/libcontainers.gpg add -
curl -L https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/$OS/Release.key | sudo apt-key --keyring /etc/apt/trusted.gpg.d/libcontainers.gpg add -

#Update apt so the new repos would be acknowledged
sudo apt-get update

#Install the following packages for the run time
sudo apt-get install cri-o cri-o-runc cri-tools -y

#Reaload systemctl 
sudo systemctl daemon-reload

#Enable crio service
sudo systemctl enable crio --now


#Install the following packages
sudo apt-get install -y apt-transport-https ca-certificates curl


#Add the k8s repo
echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list


#Get the keys to be able to donload the packages
sudo curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg



#Update apt so the new repos would be acknowledged
sudo apt-get update

#Install the following packages (Keep in mind that Kubectl should not be installed on workers)
sudo apt-get install -y kubelet kubeadm kubectl

#Hold the packages so they would not be updtaed unless specified
sudo apt-mark hold kubelet kubeadm kubectl

#On one of the masters init the cluster
kubeadm init --pod-network-cidr=192.168.0.0/16 --control-plane-endpoint IP-OF-THE-HAPROXY:6443  --upload-certs --v=5 

#If it went smoothly (which it will!) take the join commands and run on masters and workers

kubeadm join #HAPROXY-IP:6443 --token #...  \
	--discovery-token-ca-cert-hash #... 

#If you need to schedule pods on master nodes as well, run the following command 
kubectl taint nodes --all node-role.kubernetes.io/master-

#Install a CNI (Calico)
kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml



#On worker nodes, Install  the follwoing packages
apt install lvm2 unzip
dpkg -L lvm2

#Enable the following module on kernel
modprobe dm-snapshot

#Add a disk and create a partition on it
fdisk /dev/sdb 

#Create a PV on the partition
pvcreate /dev/sdb1

#Creaye a VG from the PV
vgcreate worker-1-hell /dev/sdb1


#Run the Operator deployment
kubectl apply -f Lvm-Operator-OpenEBS.yml


#create Storage class on masters and apply
kubectl apply -f sc.yaml

#Add the following key so we can donwload Helm on masters
curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | sudo tee /usr/share/keyrings/helm.gpg > /dev/null

#Add the following repo for  helm on masters
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list

#Update apt so the new repos would be acknowledged
sudo apt-get update

#Install helm on masters
sudo apt-get install helm

#Add the following repo fo Kafka project
helm repo add my-repo https://charts.bitnami.com/bitnami

#Install kafka using the custome kafka values file
helm install my-release -f values.yaml my-repo/kafka

#Chek if all the pods from worker nodes see the coredns. IF not do the following
#Disable the system resolved and 
systemctl stop systemd-resolved

#delete all coredns pods in the kube-system namespace
kubectl delete pod -n kube-system coredns #...

#Create a json file with you docker hub auth token (its called docekrconfig.json here)
#Create a secret with the json file which you just have created
kubectl create secret generic regcred     --from-file=.dockerconfigjson=dockerconfig.json     --type=kubernetes.io/dockerconfigjson


#Deploy the producer
ubectl apply -f producer-deployment.yaml 


#Deploy the consumer
kubectl apply -f consumer-deployment.yaml 


#Add prometheus helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts


#Update helm repo
helm repo update


#Create a secret for the etcd certs to get its data
kubectl create secret generic etcd-client-cert --from-file=/etc/kubernetes/pki/etcd/ca.crt --from-file=/etc/kubernetes/pki/etcd/healthcheck-client.crt --from-file=/etc/kubernetes/pki/etcd/healthcheck-client.key


#Install prometheus helm chart with the values files
helm install my-kube-prometheus-stack prometheus-community/kube-prometheus-stack --version 42.0.3 -f values.yaml


#Crate the SVC for grafana
kubectl apply -f grafananodeport.yaml 


#If you have a custome kafka exporter add it
helm upgrade my-kube-prometheus-stack prometheus-community/kube-prometheus-stack --version 42.0.3 -f custom-add-kafka-exporter.yaml


#Add the ingress repo 
 helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx


#Update helm repo
helm repo update


#Install ingress
helm install quickstart ingress-nginx/ingress-nginx


#Deploy the cert manager
kubectl apply -f https://github.com/jetstack/cert-manager/releases/download/v1.6.1/cert-manager.yaml


#Depoy the issuer to get the certificate on your behalf
kubectl apply -f cluster-issuer-email.yaml 


#Mission Accomplished


