#!/bin/bash

# 1. Enter the "Sandbox" (Virtual Environment)
source venv/bin/activate

# 2. Run the Generator
python3 generate_architecture.py

# 3. Notify User
echo "✅ Architecture Diagram updated successfully!"
