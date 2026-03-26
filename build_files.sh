# build_files.sh
echo "BUILD START"

# Use the --break-system-packages flag to bypass PEP 668
python3.12 -m pip install -r requirements.txt --break-system-packages

# Run collectstatic
python3.12 manage.py collectstatic --noinput --clear

echo "BUILD END"