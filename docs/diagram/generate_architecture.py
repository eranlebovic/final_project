import os
from diagrams import Diagram, Edge, Cluster
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
    "fontsize": "28",
    "bgcolor": "white",
    "pad": "0.5",
    "nodesep": "1.0",
    "ranksep": "2.5",
    "rankdir": "LR",
    "splines": "spline",
}

output_name = "diagram_base"
with Diagram("Ultimate DevSecOps Platform Architecture", show=False, direction="LR", graph_attr=graph_attr, filename=output_name):
    C_CI = "#EF4444"
    C_GIT = "#10B981"
    C_TRF = "#3B82F6"
    C_MGT = "#6B7280"
    C_TS = "#8B5CF6"
    C_IMG = "#F59E0B"
    C_SEC = "#DC2626"
    C_MON = "#14B8A6"

    with Cluster("1. Developer & Source"):
        github = Github("GitHub Repo\n(Source & Manifests)")
        
    with Cluster("2. Continuous Integration & Security"):
        jenkins = Jenkins("Jenkins Pipeline")
        trivy = Trivy("Trivy\n(Vuln Scanner)")
        docker_hub = Docker("Docker Hub\n(Registry)")
        
    with Cluster("3. GitOps & Infrastructure Management"):
        jumphost = Server("Jump Host / Admin")
        tf = Terraform("Terraform")
        ansible = Ansible("Ansible")
        argocd = Argocd("Argo CD\n(GitOps)")
        
    with Cluster("4. Secure Networking"):
        internet = Internet("Users / Clients")
        ts_mesh = VPN("Tailscale Mesh VPN")
        ts_infra = Pod("Tailscale Subnet Router")
        
    with Cluster("5. Proxmox Kubernetes Cluster"):
        master_api = API("Kube-API Control Plane")
        workers = Node("K8s Worker Nodes")
        
        with Cluster("Application Workloads"):
            fe_svc = Service("Frontend Service")
            fe_pods = ReplicaSet("Frontend Pods")
            
            auth_svc = Service("Auth Service")
            auth_pods = ReplicaSet("Auth Pods")
            
            be_svc = Service("Backend Service")
            be_pods = ReplicaSet("Backend Pods")
            
            db = Redis("Redis Database")
            
        with Cluster("Observability Stack"):
            prom = Prometheus("Prometheus")
            grafana = Grafana("Grafana")

    # Flow lines with numbered steps
    
    # Admin / Setup flow
    jumphost >> Edge(label="Provisions", color=C_MGT, style="dashed") >> tf
    tf >> Edge(label="Creates VMs", color=C_MGT, style="dashed") >> workers
    jumphost >> Edge(label="Configures K8s", color=C_MGT, style="dashed") >> ansible
    ansible >> Edge(label="Bootstraps", color=C_MGT, style="dashed") >> master_api

    # CI Flow
    github >> Edge(label="1", color=C_CI, penwidth="2.5") >> jenkins
    jenkins >> Edge(label="2. SAST/Scan", color=C_SEC, penwidth="2.5") >> trivy
    trivy >> Edge(label="3. Build/Push Image", color=C_CI, penwidth="2.5") >> docker_hub
    
    # GitOps Flow
    # Docker Hub updates Git via CI webhook
    docker_hub >> Edge(label="4. Update Manifest", color=C_CI, style="dotted", penwidth="2.0") >> github
    github >> Edge(label="5. Sync Desired State", color=C_GIT, penwidth="2.5") >> argocd
    argocd >> Edge(label="6. Apply Changes", color=C_GIT, penwidth="2.5") >> master_api
    master_api >> Edge(label="Schedule Pods", color=C_GIT, style="dashed") >> workers
    docker_hub >> Edge(label="Pull Container Image", color=C_IMG, style="dashed") >> workers

    # User Traffic Flow
    internet >> Edge(label="7. User Request", color=C_TRF, penwidth="2.5") >> ts_mesh
    ts_mesh >> Edge(color=C_TRF, penwidth="2.5") >> fe_svc
    fe_svc >> Edge(color=C_TRF, penwidth="2.5") >> fe_pods
    fe_pods >> Edge(label="8. Check Auth", color=C_TRF, penwidth="2.5") >> auth_svc
    auth_svc >> Edge(color=C_TRF, penwidth="2.5") >> auth_pods
    auth_pods >> Edge(label="9. API Call", color=C_TRF, penwidth="2.5") >> be_svc
    be_svc >> Edge(color=C_TRF, penwidth="2.5") >> be_pods
    be_pods >> Edge(label="10. Cache/Data", color=C_TRF, penwidth="2.5") >> db

    # Internal Networking Flow (Tailscale)
    ts_mesh >> Edge(label="Secure Admin UI", color=C_MGT) >> ts_infra
    ts_infra >> Edge(label="Internal Routing", style="dashed", color=C_TS) >> workers
    
    # Observability
    prom << Edge(label="Scrape Metrics", style="dashed", color=C_MON) << workers
    grafana << Edge(label="Query Data", style="dashed", color=C_MON) << prom
    ts_mesh >> Edge(label="View Dashboards", color=C_MON) >> grafana


# Add the left text panel
try:
    img = Image.open(f"{output_name}.png")
    
    text_content = """Ultimate DevSecOps Platform
Workflow & Automation Guide

Continuous Integration (CI)
  1. Trigger: A developer commits code and pushes to GitHub.
  2. SAST & Scan: Jenkins detects the commit, runs tests, and
      uses Trivy to scan the code/images for vulnerabilities.
  3. Build & Push: A secure Docker image is built and
      pushed to Docker Hub.
  4. Update Manifest: Jenkins updates the Kubernetes deployment
      manifests in GitHub with the new image tag.

Continuous Deployment / GitOps (CD)
  5. Sync State: Argo CD continuously monitors the GitHub repo.
      It detects the updated manifest.
  6. Apply Changes: Argo CD automatically applies the changes
      to the Proxmox Kubernetes cluster (Kube-API).
      The worker nodes then pull the new image from Docker Hub.

Application Traffic Flow (User Request)
  7. Secure Access: Users connect securely via Tailscale VPN.
      The request hits the Frontend LoadBalancer/Service.
  8. Authentication: The Frontend routes to the Auth Service
      to verify user identity and permissions.
  9. Backend Processing: Authenticated requests proceed to the
      Backend API to process business logic.
  10. Database: The Backend reads/writes to the Redis Database.

Infrastructure & Observability
  • Terraform & Ansible provision and configure the VMs.
  • Prometheus scrapes cluster metrics.
  • Grafana provides dashboards (accessed via Tailscale)."""

    panel_width = 850
    padding = 60
    
    # Calculate dimensions
    new_width = img.width + panel_width
    new_height = max(img.height, 1400)
    
    # Create the background canvas (white for the diagram side)
    final_img = Image.new('RGB', (new_width, new_height), color='#FFFFFF')
    
    # Paste the diagram on the right side (offset by panel_width), vertically centered
    paste_y = (new_height - img.height) // 2 if img.height < new_height else 0
    final_img.paste(img, (panel_width, paste_y))
    
    draw = ImageDraw.Draw(final_img)
    
    # Draw a professional solid background for the text panel (dark theme)
    # Panel background: dark slate blue
    panel_bg = "#1E293B"
    draw.rectangle([0, 0, panel_width, new_height], fill=panel_bg)
    
    # Add a subtle right border divider
    draw.line([(panel_width, 0), (panel_width, new_height)], fill="#475569", width=6)
    
    # Attempt to load fonts
    title_font = None
    body_font = None
    bold_font = None
    
    base_font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf"
    ]
    reg_font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
    ]
    
    for p in base_font_paths:
        if os.path.exists(p):
            title_font = ImageFont.truetype(p, 36)
            bold_font = ImageFont.truetype(p, 24)
            break
            
    for p in reg_font_paths:
        if os.path.exists(p):
            body_font = ImageFont.truetype(p, 23)
            break
            
    if title_font is None: title_font = ImageFont.load_default()
    if bold_font is None: bold_font = ImageFont.load_default()
    if body_font is None: body_font = ImageFont.load_default()
    
    # Render text line by line to handle bolding and colors
    y_offset = padding
    
    for line in text_content.split('\n'):
        if line.startswith("Ultimate DevSecOps"):
            draw.text((padding, y_offset), line, fill="#38BDF8", font=title_font)
            y_offset += 50
        elif line.startswith("Workflow & Automation"):
            draw.text((padding, y_offset), line, fill="#94A3B8", font=title_font)
            y_offset += 70
        elif line.strip() in ["Continuous Integration (CI)", "Continuous Deployment / GitOps (CD)", "Application Traffic Flow (User Request)", "Infrastructure & Observability"]:
            y_offset += 20 # Extra spacing before section
            draw.text((padding, y_offset), line.strip(), fill="#FCD34D", font=bold_font) # Gold color for headings
            y_offset += 45
        elif line.strip().startswith("•"):
            draw.text((padding + 20, y_offset), line.strip(), fill="#E2E8F0", font=body_font)
            y_offset += 35
        elif line.strip() == "":
            y_offset += 20
        else:
            # Check if it's a numbered item like "1. Trigger:" to bold the prefix
            line_stripped = line.strip()
            parts = line_stripped.split(":", 1)
            if len(parts) == 2 and parts[0].split('.')[0].isdigit():
                prefix = parts[0] + ":"
                rest = parts[1]
                # Draw prefix
                draw.text((padding + 20, y_offset), prefix, fill="#6EE7B7", font=bold_font)
                # Calculate width to place the rest
                prefix_bbox = draw.textbbox((padding + 20, y_offset), prefix, font=bold_font)
                prefix_width = prefix_bbox[2] - prefix_bbox[0]
                draw.text((padding + 20 + prefix_width + 12, y_offset + 1), rest, fill="#F8FAFC", font=body_font)
                y_offset += 38
            else:
                draw.text((padding + 60, y_offset), line_stripped, fill="#CBD5E1", font=body_font)
                y_offset += 38
                
    final_path = "ultimate_devsecops_platform_architecture.png"
    final_img.save(final_path)
    print(f"Successfully generated {final_path} with a beautiful dark-mode side panel.")
    
except Exception as e:
    print(f"Error adding text: {e}")