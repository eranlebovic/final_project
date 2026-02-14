Infrastructure Access Control (RBAC): For the initial provisioning phase, we utilized a root API Token with Privilege Separation disabled.

Reasoning: This ensures the Terraform provider has unrestricted access to create, modify, and destroy low-level system resources (VMs, Bridges, Storage) without hitting granular permission blockers during the prototyping phase.

Production Risk: In a real-world enterprise environment, this violates the Principle of Least Privilege.

Remediation: For a strict production setup, we would create a dedicated terraform-service-account user in Proxmox and assign it a custom role (e.g., TerraformProv) limiting it strictly to VM creation only, rather than full system root access.

NAME            STATUS   ROLES           AGE   VERSION
k8s-master      Ready    control-plane   17h   v1.29.15
k8s-worker-01   Ready    <none>          17h   v1.29.15
k8s-worker-02   Ready    <none>          17h   v1.29.15
k8s-worker-03   Ready    <none>          61m   v1.29.15
