from diagrams import Cluster, Diagram, Edge
from diagrams.onprem.compute import Server
from diagrams.onprem.network import Internet
from diagrams.onprem.vcs import Github
from diagrams.onprem.ci import Jenkins
from diagrams.onprem.container import Docker
from diagrams.onprem.gitops import Argocd          
from diagrams.k8s.controlplane import API, CM, Scheduler
from diagrams.k8s.infra import Node
from diagrams.k8s.compute import Pod, ReplicaSet
from diagrams.k8s.network import Service
from diagrams.onprem.inmemory import Redis
from diagrams.generic.network import VPN
from diagrams.onprem.iac import Terraform, Ansible
from diagrams.onprem.security import Trivy
from diagrams.onprem.monitoring import Prometheus, Grafana

# Force strict Left-to-Right layout with wider spacing to prevent arrow overlaps
graph_attr = {
    "fontsize": "22",
    "bgcolor": "white",
    "pad": "0.5",
    "nodesep": "0.7",
    "ranksep": "1.2",
    "rankdir": "LR",       
    "splines": "spline"    
}

with Diagram("Ultimate DevSecOps Platform Architecture", show=False, direction="LR", graph_attr=graph_attr):
    
    # --- COLOR GLOSSARY ---
    C_CI = "firebrick"    # CI/CD Pipeline
    C_GIT = "darkgreen"   # GitOps Sync
    C_TRF = "blue"        # User/App Traffic
    C_MGT = "grey"        # Admin/Management
    C_TS = "purple"       # Tailscale Operations
    C_IMG = "orange"      # Image Pulls
    C_SEC = "red"         # Security Flow
    C_MON = "teal"        # Monitoring Flow

    # --- OUTSIDE K8S ---
    internet = Internet("User Traffic")
    ts_mesh = VPN("Tailscale Mesh\n(100.x.x.x)")
    
    with Cluster("External Cloud"):
        github = Github("GitHub Repo")
        docker_hub = Docker("Docker Hub")

    with Cluster("Home Network (192.168.1.x)"):
        with Cluster("Jump Host & IaC"):
            jumphost = Server("Jump Host\n192.168.1.244")
            tf = Terraform("Terraform")
            ansible = Ansible("Ansible")
            
        with Cluster("CI/CD Pipeline"):
            jenkins = Jenkins("Jenkins CI")
            trivy = Trivy("Trivy Scanner\n(Image Scan)")

        # --- KUBERNETES CLUSTER ---
        with Cluster("Proxmox K8s Cluster (v1.29)"):
            
            # Column 1: Management & Ingress
            ts_infra = Pod("Tailscale Infra\n(Operator & Connectors)")
            argocd = Argocd("Argo CD")

            # Column 2: Control Plane & Observability
            master_api = API("Kube-API\n(Master)")
            with Cluster("Monitoring Cluster"):
                prom = Prometheus("Prometheus")
                grafana = Grafana("Grafana")
            
            # Column 3: Workloads & Nodes
            with Cluster("Environments (devops-prod / devops-dev)"):
                with Cluster("Frontend Helm Chart"):
                    fe_svc = Service("Frontend LB\n(devops-frontend)")
                    fe_pods = ReplicaSet("Frontend Pods\n(x3)")
                
                with Cluster("Auth Service Helm Chart"):
                    auth_svc = Service("Auth LB\n(devops-auth)")
                    auth_pods = ReplicaSet("Auth Pods\n(x2)")

                with Cluster("Backend Helm Chart"):
                    be_svc = Service("Backend LB\n(devops-backend)")
                    be_pods = ReplicaSet("Backend Pods\n(x3)")
                    db = Redis("Redis DB")

            with Cluster("Worker Nodes"):
                workers = Node("K8s Workers\n(01, 02, 03)")

    # --- EXPLICIT FLOW LAYOUT ---
    
    # IaC Provisioning Flow
    jumphost >> Edge(label="Provisions", color=C_MGT, style="dotted") >> tf
    tf >> Edge(label="Creates VMs", color=C_MGT, style="dotted") >> workers
    jumphost >> Edge(label="Configures K8s", color=C_MGT, style="dashed") >> ansible
    ansible >> Edge(label="Bootstraps", color=C_MGT, style="dashed") >> master_api

    # 1. CI/CD Flow (Red)
    github >> Edge(label="1. Trigger", color=C_CI) >> jenkins
    jenkins >> Edge(label="2. SAST/Scan", color=C_SEC) >> trivy
    trivy >> Edge(label="3. Build/Push", color=C_CI) >> docker_hub
    jenkins >> Edge(label="4. GitOps Update", color=C_CI) >> github

    # 2. GitOps Flow (Green)
    github >> Edge(label="5. Sync", color=C_GIT, style="bold") >> argocd
    argocd >> Edge(label="6. Apply", color=C_GIT, style="bold") >> master_api
    docker_hub >> Edge(label="Pull Image", color=C_IMG, style="dashed") >> workers

    # 3. Traffic Flow (Blue)
    internet >> Edge(color=C_TRF) >> ts_mesh
    ts_mesh >> Edge(label="Web Request", color=C_TRF) >> fe_svc
    fe_svc >> Edge(color=C_TRF) >> fe_pods
    fe_pods >> Edge(label="API Call via Tailscale DNS", color=C_TRF) >> auth_svc
    auth_svc >> Edge(color=C_TRF) >> auth_pods
    auth_pods >> Edge(label="Auth & Verify", color=C_TRF) >> be_svc
    be_svc >> Edge(color=C_TRF) >> be_pods
    be_pods >> Edge(label="Read/Write", color=C_TRF) >> db

    # 4. Tailscale & Admin Flows (Grey/Purple)
    ts_infra >> Edge(label="Configures LB", style="dotted", color=C_TS) >> fe_svc
    ts_infra >> Edge(style="dotted", color=C_TS) >> auth_svc
    ts_infra >> Edge(style="dotted", color=C_TS) >> be_svc
    
    jumphost >> Edge(label="Admin UI / CLI", color=C_MGT) >> ts_mesh
    jumphost >> Edge(label="Direct SSH", color=C_MGT) >> ts_infra
    ts_infra >> Edge(label="Routes to Node IPs", style="dotted", color=C_MGT) >> workers

    # 5. Monitoring
    prom >> Edge(label="Scrape Metrics", style="dotted", color=C_MON) >> workers
    grafana >> Edge(label="Query Metrics", style="dotted", color=C_MON) >> prom