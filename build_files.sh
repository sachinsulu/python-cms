#!/bin/bash
echo "BUILD START"

# Install dependencies
python3.12 -m pip install -r requirements.txt --break-system-packages

# Collect static files
python3.12 manage.py collectstatic --noinput --clear

echo "BUILD END"