if ! grep -q FLASK_RUN_PORT ".env" || ! [[ -d vlab ]]; then
    echo Run setup.sh first
    exit 1
fi


app=$1

if [[ -z $app ]]; then
    app=lab1
fi

# activate the virtual environment for the lab
source vlab/bin/activate

# run Flask for lab1
echo Running Flask
FLASK_APP=$app flask run

