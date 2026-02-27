#!/bin/bash


# 1. Navigate to the diagram directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 2. Run the Generator
python3 generate_architecture.py

# 3. Notify User
echo "✅ Architecture Diagram updated successfully!"
