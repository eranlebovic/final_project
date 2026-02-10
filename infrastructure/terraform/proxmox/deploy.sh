#!/bin/bash

# Define Colors for pretty output
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# 1. Run Terraform
echo -e "${CYAN}🚀 Provisioning Infrastructure...${NC}"
terraform apply -parallelism=1 -auto-approve

# 2. Wait for HDDs to settle
echo -e "${YELLOW}⏳ Waiting 10 seconds for storage to settle...${NC}"
sleep 10

# 3. Force Start VMs (SSH to Proxmox)
PVE_HOST="100.91.241.119"

echo -e "${GREEN}⚡ Force Starting VMs...${NC}"
# Note: This requires your Jump Host to have SSH access to the Proxmox Host (Root)
ssh root@$PVE_HOST "qm start 200; qm start 201; qm start 202; qm start 100"

echo -e "${GREEN}✅ Deployment Complete!${NC}"
