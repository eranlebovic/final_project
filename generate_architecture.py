from diagrams import Cluster, Diagram, Edge
from diagrams.onprem.compute import Server
from diagrams.onprem.network import Internet
from diagrams.onprem.vcs import Github
from diagrams.onprem.ci import Jenkins          # <-- Added
from diagrams.onprem.container import Docker    # <-- Added
from diagrams.k8s.controlplane import API, CM, Scheduler
from diagrams.k8s.infra import Node
from diagrams.k8s.compute import Pod
from diagrams.k8s.network import Service
from diagrams.k8s.podconfig import Secret
from diagrams.onprem.inmemory import Redis

graph_attr = {
    "fontsize": "25",
    "bgcolor": "white",
    "pad": "0.5"
}

# The Title below determines the filename. 
# Keeping it "Ultimate DevSecOps..." ensures we update your EXISTING file.
with Diagram("Ultimate DevSecOps Platform Architecture", show=False, graph_attr=graph_attr):
    
    # --- External Services ---
    internet = Internet("User Traffic")
    
    with Cluster("External SaaS / Cloud"):
        github = Github("GitHub Repo")
        docker_hub = Docker("Docker Hub")

    # --- On-Premises Network ---
    with Cluster("Home Network (192.168.1.x)"):
        
        # Jump Host / CI Server Section
        with Cluster("Management & CI/CD"):
            jumphost = Server("Jump Host\n192.168.1.244")
            jenkins = Jenkins("Jenkins LTS")
            
            # Jenkins runs ON the Jump Host
            jumphost - Edge(style="dotted") - jenkins 

        # Proxmox / Kubernetes Section
        with Cluster("Proxmox Virtual Environment"):
            with Cluster("Kubernetes Cluster (v1.29)"):
                
                # Master Node
                with Cluster("Master Node\n192.168.1.164"):
                    master_api = API("Kube-API")
                    master_comp = [CM("Controller"), Scheduler("Sched")]

                # Worker Nodes
                with Cluster("Worker Nodes"):
                    workers = [Node("Worker-01\n.129"), Node("Worker-02\n.142"), Node("Worker-03\n.134")]

                # Applications
                with Cluster("Application Workloads"):
                    frontend = [Pod("UI-1"), Pod("UI-2"), Pod("UI-3")]
                    backend = [Pod("API-1"), Pod("API-2"), Pod("API-3")]
                    db = Redis("Redis DB")
                    
                    fe_svc = Service("NodePort:30002")
                    be_svc = Service("NodePort:30001")
                    cred = Secret("Redis-Secret")

    # --- LOGICAL FLOWS ---
    github >> Edge(label="Git Pull", color="firebrick") >> jenkins
    jenkins >> Edge(label="Build & Push", color="firebrick") >> docker_hub
    jenkins >> Edge(label="Deploy", color="firebrick") >> master_api
    docker_hub >> Edge(label="Image Pull", color="orange", style="dashed") >> workers

    internet >> Edge(label="HTTPS", color="blue") >> fe_svc >> frontend
    frontend >> Edge(label="API Call", color="blue") >> be_svc >> backend
    backend >> Edge(label="Read/Write", color="blue") >> db
    backend >> Edge(label="Auth", style="dashed") >> cred
    
    jumphost >> Edge(label="SSH/Ansible", color="green") >> master_api