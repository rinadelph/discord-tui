#!/bin/bash
cd /home/alejandro/discordo-python
python3 main.py "$@" 2>&1 | tee app_run.log
echo ""
echo "================================================================================"
echo "Log saved to: /home/alejandro/discordo-python/app_run.log"
echo "================================================================================"
