provider "ibm" {
  softlayer_username = "${var.sl_username}"
  softlayer_api_key = "${var.sl_api_key}"
  # endpoint_url = "https://api.softlayer.com/xmlrpc/v3.1/"
}

resource "ibm_compute_ssh_key" "default" {
  label = "${var.sl_key_name}"
  public_key = "${file(var.public_key_path)}"
}
