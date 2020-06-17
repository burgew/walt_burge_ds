provider "ibm" {
  softlayer_username = "<enter user name>"
  softlayer_api_key = "<enter api key>"
}

data "ibm_compute_ssh_key" "my_key" {
    label = "${var.ssh_key_label}"
}

resource "ibm_compute_vm_instance" "manager" {
    hostname          = "docker-swarm-manager"
    domain            = "final.w251.mids"
    os_reference_code = "UBUNTU_16_64"
    datacenter        = "${var.datacenter}"
    cores             = 1
    memory            = 1024
    local_disk        = true
    disks             = [25]

    ssh_key_ids = [
        "${data.ibm_compute_ssh_key.my_key.id}"
    ]
    
    connection {
    type = "ssh"
    user = "root"
    private_key = "${file("~/.ssh/id_rsa")}"
    }

    provisioner "remote-exec" {
        script = "docker.sh"
    }

    provisioner "local-exec" {
        command = "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@${self.ipv4_address} 'docker swarm join-token -q worker' > token.txt"
    }
}

resource "ibm_network_public_ip" "manager-ip" {
    routes_to = "${ibm_compute_vm_instance.manager.ipv4_address}"
}

resource "ibm_network_public_ip" "manager-ip" {
    routes_to = "${ibm_compute_vm_instance.manager.ipv4_address}"
}

resource "ibm_compute_vm_instance" "worker" {
    count             = "${var.worker_count}"
    hostname          = "docker-swarm-worker${count.index}"
    domain            = "final.w251.mids"
    os_reference_code = "UBUNTU_16_64"
    datacenter        = "${var.datacenter}"
    cores             = 1
    memory            = 1024
    local_disk        = true
    disks             = [25]

    ssh_key_ids = [
        "${data.ibm_compute_ssh_key.my_key.id}"
    ]
    
    connection {
    type = "ssh"
    user = "root"
    private_key = "${file("~/.ssh/id_rsa")}"
    }

    provisioner "remote-exec" {
        inline = [
            "apt-get update -y > /dev/null",
            "apt-get install docker.io curl -y",
            "curl -L http://bit.ly/2kuCjmp | bash -s",
            "ufw allow 2377/tcp",
            "ufw allow 4789/tcp",
            "ufw allow 7946/tcp",
            "docker swarm join --token ${trimspace(file("token.txt"))} ${ibm_compute_vm_instance.manager.ipv4_address}:2377"
        ]
    }
}
