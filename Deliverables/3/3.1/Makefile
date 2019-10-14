all:
	echo running makefile
	sudo apt-get update
	-sudo apt-get install python3 python3-pip
	-sudo python3 -m pip install --user virtualenv
	-sudo python3 -m virtualenv venv
	-. venv/bin/activate 
	-pip install --user -r requirements.txt
