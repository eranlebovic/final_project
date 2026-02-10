# --- K8s Cluster Nodes ---
resource "proxmox_virtual_environment_vm" "k8s_nodes" {
  count     = 3 # Change this to 4 when you are ready to add a node!
  name      = count.index == 0 ? "k8s-master" : "k8s-worker-0${count.index}"
  node_name = "pve"
  vm_id     = 200 + count.index

  # --- FIX 1: IGNORE THE VGA CHANGES ---
  lifecycle {
    ignore_changes = [
      initialization,
      disk,
      network_device,
      vga,  # <--- ADD THIS! Tells Terraform "Don't touch the display adapter"
    ]
  }

  cpu {
    cores = 4
    type  = "host"
  }

  memory {
    dedicated = 8192
  }

  clone {
    vm_id = 9000
  }

  disk {
    datastore_id = "Storage"
    interface    = "scsi0"
    size         = 50
    file_format  = "raw"
  }

  network_device {
    bridge = "vmbr0"
  }

  initialization {
    # --- FIX 2: FORCE CLOUD-INIT TO USE YOUR STORAGE ---
    datastore_id = "Storage" # <--- ADD THIS! Prevents the move to "local-lvm"

    ip_config {
      ipv4 {
        address = "dhcp"
      }
    }
    
    user_account {
      username = "ubuntu"
      password = "Password123!"
      keys     = [var.ssh_public_key]
    }
  }

  # --- FIX 3: DEFINE THE VGA EXPLICITLY (Optional but Good) ---
  vga {
    type   = "serial0"
    memory = 16
  }
}

variable "ssh_public_key" {
  type = string
}