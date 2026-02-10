from diagrams import Cluster, Diagram, Edge
from diagrams.onprem.compute import Server
from diagrams.onprem.container import Docker
from diagrams.onprem.database import Mongodb, Postgresql
from diagrams.onprem.inmemory import Redis
from diagrams.onprem.monitoring import Grafana, Prometheus
from diagrams.onprem.network import Nginx, Haproxy
from diagrams.onprem.vcs import Github
from diagrams.onprem.ci import Jenkins
from diagrams.onprem.gitops import Argocd  # Corrected Import Path
from diagrams.onprem.iac import Terraform
from diagrams.aws.storage import S3
from diagrams.aws.network import Route53
from diagrams.k8s.compute import Pod

# Attributes for the diagram
graph_attr = {
    "fontsize": "20",
    "bgcolor": "white"
}

with Diagram("Ultimate DevSecOps Platform Architecture", show=False, direction="LR", graph_attr=graph_attr):

    with Cluster("Developer Workstation (Windows)"):
        dev = Server("You")
        tf = Terraform("IaC Code")
        
    with Cluster("AWS Cloud (Free Tier)"):
        dns = Route53("DNS Zone")
        tf_state = S3("Terraform State")

    with Cluster("CI/CD Pipeline"):
        git = Github("Git Repo")
        ci = Jenkins("CI Server")
        registry = Docker("Image Registry")
        gitops = Argocd("ArgoCD")

    with Cluster("Proxmox Home Lab (Ryzen 9 9950x)"):
        
        with Cluster("Kubernetes Cluster"):
            monitor = Prometheus("Prometheus")
            viz = Grafana("Grafana")
            
            with Cluster("Ingress Layer"):
                # Using Haproxy to represent Load Balancer
                lb = Haproxy("MetalLB") 
                ingress = Nginx("Ingress Controller")

            with Cluster("Microservices Tier"):
                fe = Pod("Frontend")
                be = Pod("Backend API")
                auth = Pod("Auth Service")

            with Cluster("Data Persistence"):
                db_sql = Postgresql("PostgreSQL")
                db_nosql = Mongodb("MongoDB")
                cache = Redis("Redis")

    # Workflow Connections
    dev >> Edge(label="Push Code") >> git
    dev >> Edge(label="Provision") >> tf
    tf >> Edge(label="State Store") >> tf_state
    
    # CI Flow
    git >> Edge(label="Trigger") >> ci
    ci >> Edge(label="Build & Scan") >> registry
    
    # CD Flow
    gitops >> Edge(label="Watch") >> git
    gitops >> Edge(label="Sync") >> ingress

    # User Traffic Flow
    user_traffic = Edge(color="firebrick", style="dashed")
    dns >> user_traffic >> lb >> user_traffic >> ingress
    ingress >> user_traffic >> fe
    fe >> user_traffic >> be
    be >> user_traffic >> db_sql
    be >> user_traffic >> cache

    # Monitoring
    monitor >> Edge(style="dotted") >> [fe, be, db_sql]
    viz >> monitor