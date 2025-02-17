#!/usr/bin/env bash
# remember to run chmod +x post-create.sh
set -euo pipefail
[[ ${DEBUG-} =~ ^1|yes|true$ ]] && set -o xtrace

# Update APT packages and install MESA GLX support
#sudo apt update
#sudo apt install -y libgl1-mesa-glx
pip install --upgrade pip
pip install -r requirements.txt