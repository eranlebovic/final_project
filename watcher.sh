#!/bin/bash

# Configuration
TARGET_DIR="/opt/final_project"
WATCH_FILE="generate_architecture.py"
VENV_PYTHON="$TARGET_DIR/venv/bin/python3"

echo "👀 Watcher started: Monitoring $WATCH_FILE..."

# inotifywait will block and wait for a 'save' event
inotifywait -m -e close_write "$TARGET_DIR" |
while read -r directory events filename; do
    if [ "$filename" = "$WATCH_FILE" ]; then
        # 1. Clear the noise
        clear
        echo -e "\033[1;33m[ PROCESSING ] Generating new architecture... \033[0m"

        # 2. Run the generator
        $VENV_PYTHON "$TARGET_DIR/$WATCH_FILE"
        
        if [ $? -eq 0 ]; then
            # 3. THE VISUAL ALARM
            echo -e "\033[1;32m"
            cat << "EOF"
##########################################################
#                                                        #
#   🔔  ALARM: ARCHITECTURE SKETCH UPDATED!              #
#                                                        #
##########################################################
EOF
            echo -e "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
            echo -e "\033[0m"
        else
            echo -e "\033[1;31m[ ERROR ] Diagram generation failed!\033[0m"
        fi # Closes inner if
        
        echo "Waiting for next change..."
    fi # Closes outer if
done # Closes while loop
