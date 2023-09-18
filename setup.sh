portnum=5${USER: -4}
if [ "$1" = "--port" ]; then
  portnum="$2"
fi

# add the FLASK RUN PORT to .env if it doesn't alrady exist
if ! grep -q FLASK_RUN_PORT ".env"; then
    echo Creating .env
    echo FLASK_ENV=development >.env
    echo FLASK_RUN_PORT=$portnum >> .env
fi

# add virtual environment if it doesn't already exist
if ! [[ -d vlab ]]; then
    echo Adding virtual environment 
    python3 -m venv vlab

    # create pip.conf if doesn't exist
    echo Creating vlab/pip.conf
    ( cat <<'EOF'
[install]
user = false
EOF
    ) > vlab/pip.conf

    source vlab/bin/activate

    echo Setting up Flask requirements
    pip install -r requirements.txt
    deactivate
fi

# activate the virtual environment for the lab
source vlab/bin/activate

# run Flask for lab1
./run.sh lab3