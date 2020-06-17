#!/bin/bash
set -e  # Exit if anything returns an error

# Create the final "variables.tf" file which will be used to terraform the cluster
cat variables_base._tf > variables.tf
cat count_kafka._tf >> variables.tf
# ... repeat for each service...

# Show the cluster plan
terraform plan

# Confirmation prompt
read -p "Would you like to build the cluster using these settings? " -n 1 -r
echo  # print new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
  terraform build
fi
