from diagrams import Cluster, Diagram, Edge
from diagrams.onprem.compute import Server
from diagrams.onprem.network import Internet
from diagrams.onprem.vcs import Github
from diagrams.k8s.controlplane import API, CM, Scheduler
from diagrams.k8s.infra import Node
from diagrams.k8s.compute import Pod

# Define the diagram attributes
graph_attr = {
    "fontsize": "25",
    "bgcolor": "white"
}

with Diagram("Ultimate DevSecOps Platform Architecture", show=False, graph_attr=graph_attr):

    internet = Internet("Internet")
    github = Github("GitHub Repo\n(CI/CD Config)")

    with Cluster("Home Network (192.168.1.x)"):
        
        # Jump Host (Your Control Center)
        # Using .244 based on your recent nmap scan
        jumphost = Server("Jump Host\n100.103.55.39")

        with Cluster("Proxmox Virtual Environment"):
            
            # Kubernetes Cluster
            with Cluster("Kubernetes Cluster (v1.29)"):
                
                # Master Node
                with Cluster("Master Node\n192.168.1.164"):
                    master = API("Kube-API")
                    cm = CM("Controller\nManager")
                    sched = Scheduler("Scheduler")
                    
                    # Master Components Talk to Each Other
                    master - Edge(color="blue", style="dotted") - cm
                    master - Edge(color="blue", style="dotted") - sched

                # Worker Nodes
                with Cluster("Worker Nodes"):
                    worker1 = Node("Worker-01\n.129")
                    worker2 = Node("Worker-02\n.142")
                    worker3 = Node("Worker-03\n.134")
                    
                    workers = [worker1, worker2, worker3]

    # --- Connections ---

    # 1. External Access
    internet >> Edge(label="Git Push") >> github
    github >> Edge(label="Pull Playbooks") >> jumphost

    # 2. Jump Host Management (Ansible Control)
    # This line creates a red arrow to all three workers at once
    jumphost >> Edge(label="Ansible (SSH)", color="red") >> workers
    jumphost >> Edge(label="Ansible (SSH)", color="red") >> master
    
    # 3. Kubectl Control
    jumphost >> Edge(label="kubectl (API)", color="green") >> master

    # 4. Cluster Communication (Master to Workers)
    master >> Edge(label="Kubelet Control", color="blue") >> workers
# Last updated: Wed Feb 11 05:04:55 PM UTC 2026
# Last updated: Wed Feb 11 05:06:10 PM UTC 2026
# Last updated: Wed Feb 11 05:12:51 PM UTC 2026
