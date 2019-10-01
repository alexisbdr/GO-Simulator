all:
  echo sample makefile is running
  sudo apt-get update
  -sudo apt-get install python3.8
  -sudo apt-get install python3-pip
  -pip install requirements.txt
  cp python_folder ./
  cp run.sh ./
