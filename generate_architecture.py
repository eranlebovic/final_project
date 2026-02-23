import os
from diagrams import Diagram, Edge
from diagrams.onprem.compute import Server
from diagrams.onprem.network import Internet
from diagrams.onprem.vcs import Github
from diagrams.onprem.ci import Jenkins
from diagrams.onprem.container import Docker
from diagrams.onprem.gitops import Argocd          
from diagrams.k8s.controlplane import API
from diagrams.k8s.infra import Node
from diagrams.k8s.compute import Pod, ReplicaSet
from diagrams.k8s.network import Service
from diagrams.onprem.inmemory import Redis
from diagrams.generic.network import VPN
from diagrams.onprem.iac import Terraform, Ansible
from diagrams.onprem.security import Trivy
from diagrams.onprem.monitoring import Prometheus, Grafana
from PIL import Image, ImageDraw, ImageFont

# Set attributes for the main diagram
graph_attr = {
    "fontsize": "24",
    "bgcolor": "white",
    "pad": "1.0",
    "nodesep": "0.8",
    "ranksep": "1.5",
    "rankdir": "LR"
}

output_name = "diagram_base"
with Diagram("Ultimate DevSecOps Platform Architecture", show=False, direction="LR", graph_attr=graph_attr, filename=output_name):
    C_CI = "firebrick"
    C_GIT = "darkgreen"
    C_TRF = "blue"
    C_MGT = "grey"
    C_TS = "purple"
    C_IMG = "orange"
    C_SEC = "red"
    C_MON = "teal"

    # Flat nodes without clusters to avoid Graphviz init_rank bugs
    internet = Internet("User Traffic")
    ts_mesh = VPN("Tailscale Mesh")
    github = Github("GitHub Repo")
    docker_hub = Docker("Docker Hub")
    jumphost = Server("Jump Host")
    tf = Terraform("Terraform")
    ansible = Ansible("Ansible")
    jenkins = Jenkins("Jenkins CI")
    trivy = Trivy("Trivy Scanner")
    ts_infra = Pod("Tailscale Infra")
    argocd = Argocd("Argo CD")
    master_api = API("Kube-API")
    prom = Prometheus("Prometheus")
    grafana = Grafana("Grafana")
    fe_svc = Service("Frontend LB")
    fe_pods = ReplicaSet("Frontend Pods")
    auth_svc = Service("Auth LB")
    auth_pods = ReplicaSet("Auth Pods")
    be_svc = Service("Backend LB")
    be_pods = ReplicaSet("Backend Pods")
    db = Redis("Redis DB")
    workers = Node("Workers")

    # Flow lines with numbered steps
    jumphost >> Edge(label="Provisions", color=C_MGT, style="dotted") >> tf
    tf >> Edge(label="Creates VMs", color=C_MGT, style="dotted") >> workers
    jumphost >> Edge(label="Configures K8s", color=C_MGT, style="dashed") >> ansible
    ansible >> Edge(label="Bootstraps", color=C_MGT, style="dashed") >> master_api

    github >> Edge(label="1. Trigger", color=C_CI) >> jenkins
    jenkins >> Edge(label="2. SAST/Scan", color=C_SEC) >> trivy
    trivy >> Edge(label="3. Build/Push", color=C_CI) >> docker_hub
    jenkins >> Edge(label="4. GitOps Update", color=C_CI) >> github

    github >> Edge(label="5. Sync", color=C_GIT, style="bold") >> argocd
    argocd >> Edge(label="6. Apply", color=C_GIT, style="bold") >> master_api
    docker_hub >> Edge(label="Pull Image", color=C_IMG, style="dashed") >> workers

    internet >> Edge(label="7", color=C_TRF) >> ts_mesh
    ts_mesh >> Edge(label="7. Web Request", color=C_TRF) >> fe_svc
    fe_svc >> Edge(color=C_TRF) >> fe_pods
    fe_pods >> Edge(label="8. API Call", color=C_TRF) >> auth_svc
    auth_svc >> Edge(color=C_TRF) >> auth_pods
    auth_pods >> Edge(label="9. Auth/Verify", color=C_TRF) >> be_svc
    be_svc >> Edge(color=C_TRF) >> be_pods
    be_pods >> Edge(label="10. Read/Write", color=C_TRF) >> db

    ts_infra >> Edge(label="Configures LB", style="dotted", color=C_TS) >> fe_svc
    ts_infra >> Edge(style="dotted", color=C_TS) >> auth_svc
    ts_infra >> Edge(style="dotted", color=C_TS) >> be_svc
    
    jumphost >> Edge(label="Admin UI / CLI", color=C_MGT) >> ts_mesh
    jumphost >> Edge(label="Direct SSH", color=C_MGT) >> ts_infra
    ts_infra >> Edge(label="Routes to Node IPs", style="dotted", color=C_MGT) >> workers

    prom >> Edge(label="Scrape Metrics", style="dotted", color=C_MON) >> workers
    grafana >> Edge(label="Query Metrics", style="dotted", color=C_MON) >> prom

# Now append the text box to the left side using Pillow
try:
    img = Image.open(f"{output_name}.png")
    
    text_content = (
        "Project Architecture Flow (Left-to-Right):\n\n"
        "1. Dev pushes code:\n   Developer writes code and commits it to the GitHub repository.\n\n"
        "2. CI builds & runs Trivy:\n   Jenkins automatically detects the change, tests the app, \n   and scans for security vulnerabilities.\n\n"
        "3. Push Image to DockerHub:\n   The built application is packaged as a Docker image and uploaded securely.\n\n"
        "4. CI updates Git:\n   Jenkins updates the Kubernetes manifests in GitHub with the new image tag.\n\n"
        "5. Argo CD detects & applies:\n   Argo CD sees the Git change and syncs the Kubernetes cluster to match.\n\n"
        "6. Cluster pulls new image:\n   Kubernetes downloads the new Docker image onto the worker nodes directly.\n\n"
        "7. User accesses via Tailscale:\n   A user connects securely to the application through the Tailscale VPN mesh.\n\n"
        "8-10. Request flows FE -> Auth -> BE -> DB:\n   The request hits the Frontend, checks Auth, calls Backend, and reads Redis."
    )
    
    panel_width = 850
    new_width = img.width + panel_width
    new_height = max(img.height, 1200)
    
    final_img = Image.new('RGB', (new_width, new_height), color='white')
    
    paste_y = (new_height - img.height) // 2 if img.height < new_height else 0
    final_img.paste(img, (panel_width, paste_y))
    
    draw = ImageDraw.Draw(final_img)
    
    font = None
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
    ]
    for p in font_paths:
        if os.path.exists(p):
            font = ImageFont.truetype(p, 28)
            break
            
    if font is None:
        font = ImageFont.load_default()
    
    draw.rectangle([20, 20, panel_width-20, new_height-20], outline="black", width=2)
    draw.text((40, 40), text_content, fill="black", font=font, align="left")
    
    final_path = "ultimate_devsecops_platform_architecture.png"
    final_img.save(final_path)
    print(f"Successfully generated {final_path} with left-aligned text.")
    
except Exception as e:
    print(f"Error adding text: {e}")