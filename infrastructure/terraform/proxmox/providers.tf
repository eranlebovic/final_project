terraform {
  required_providers {
    proxmox = {
      source  = "bpg/proxmox"
      version = "0.66.1"
    }
  }
}

provider "proxmox" {
  endpoint = var.proxmox_api_url
  
  # The bpg provider uses 'api_token', NOT 'pm_api_token_id'
  api_token = "${var.proxmox_api_token_id}=${var.proxmox_api_token_secret}"
  
  insecure = true
  
  ssh {
    agent = true
  }
}

# --- Fixed Variable Definitions (No Semicolons) ---

variable "proxmox_api_url" {
  type = string
}

variable "proxmox_api_token_id" {
  type = string
}

variable "proxmox_api_token_secret" {
  type      = string
  sensitive = true
}