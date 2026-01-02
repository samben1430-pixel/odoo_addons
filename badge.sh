#!/bin/bash
# Script raccourci pour lancer la gestion du badgeage

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

python3 "$SCRIPT_DIR/gestion_badgeage.py" "$@"
