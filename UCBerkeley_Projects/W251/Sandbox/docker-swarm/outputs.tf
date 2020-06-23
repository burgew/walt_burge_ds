output "manager node ip" {
  value = "${ibm_network_public_ip.manager-ip.ip_address}"
}
