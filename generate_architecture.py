from diagrams import Cluster, Diagram, Edge
from diagrams.onprem.compute import Server
from diagrams.onprem.network import Internet
from diagrams.onprem.vcs import Github
from diagrams.k8s.controlplane import API, CM, Scheduler
from diagrams.k8s.infra import Node
from diagrams.k8s.compute import Pod, Deployment
from diagrams.k8s.network import Service
from diagrams.k8s.podconfig import Secret
from diagrams.onprem.inmemory import Redis  # <-- Fixed: Redis is 'inmemory'

graph_attr = {
    "fontsize": "25",
    "bgcolor": "white"
}

with Diagram("Ultimate DevSecOps Platform Architecture", show=False, graph_attr=graph_attr):
    internet = Internet("Internet")
    github = Github("GitHub Repo")

    with Cluster("Home Network (192.168.1.x)"):
        jumphost = Server("Jump Host\n192.168.1.244")

        with Cluster("Proxmox Virtual Environment"):
            with Cluster("Kubernetes Cluster (v1.29)"):
                with Cluster("Master Node\n192.168.1.164"):
                    master_api = API("Kube-API")
                    master_comp = [CM("Controller"), Scheduler("Sched")]

                with Cluster("Worker Nodes"):
                    workers = [Node("Worker-01\n.129"), 
                               Node("Worker-02\n.142"), 
                               Node("Worker-03\n.134")]

                with Cluster("Application Workloads"):
                    # Showing 3 replicas for HA across workers
                    frontend = [Pod("UI-1"), Pod("UI-2"), Pod("UI-3")]
                    backend = [Pod("API-1"), Pod("API-2"), Pod("API-3")]
                    db = Redis("Redis DB")
                    
                    fe_svc = Service("NodePort:30002")
                    be_svc = Service("NodePort:30001")
                    cred = Secret("Redis-Secret")

    # Flow
    internet >> Edge(label="HTTPS") >> fe_svc >> frontend
    frontend >> Edge(label="API Call") >> be_svc >> backend
    backend >> Edge(label="Read/Write") >> db
    backend >> Edge(label="Auth", style="dashed") >> cred
    
    # Management
    jumphost >> Edge(label="kubectl", color="green") >> master_api
    master_api >> Edge(label="Control", color="blue") >> workers
