#!/bin/bash

# Install Terraform
yum install -y unzip
wget -O terraform.zip https://releases.hashicorp.com/terraform/0.11.7/terraform_0.11.7_linux_amd64.zip
unzip terraform.zip
mv terraform /usr/bin
rm -f terraform.zip

# Install the IBM Provider binary
wget -O terraform.ibm.zip https://github.com/IBM-Cloud/terraform-provider-ibm/releases/download/v0.11.1/linux_amd64.zip
unzip terraform.ibm.zip
mkdir -p /root/.terraform
mv terraform-provider-ibm /root/.terraform
rm -f terraform.ibm.zip

# Write the terraformrc config file so Terraform can find the IBM provider
cat > ~/.terraformrc << EOF
providers {
  ibm = "/root/.terraform/terraform-provider-ibm"
}
EOF

