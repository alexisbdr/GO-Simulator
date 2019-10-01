all:
  echo sample makefile is running
  sudo apt-get update
  -sudo apt-get install python3.8
  -sudo apt-get install python3-pip
  cp requirements.txt ./
  -pip install -r requirements.txt 
  cp python_folder ./
  cp run.sh ./
