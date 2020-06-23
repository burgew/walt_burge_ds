variable "sl_api_key" {
  description = "Your SoftLayer API key"
}

variable "sl_username" {
  description = "Your SoftLayer username ID"
}

variable "public_key_path" {
  description = "Path to the SSH public key used for authentication"
}

variable "sl_key_name" {
  description = "Name of the key on SoftLayer"
  default = "terraform"
}
