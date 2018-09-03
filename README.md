# Airbnb's crawler

## How to setup??

### move to bnbch directory
cd /xxx/bnbch

## create a folder saving files including csv, tsv, json
mkdir csv

## You must install Google-chrome, chromedriver, selenium in order to run Airbnb's crawler...
### install Google-chrome  
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt update
sudo apt -f install -y

### install chromedriver
#if you need "unzip"
sudo apt install unzip 
wget https://chromedriver.storage.googleapis.com/<chromedriver version (ex. 2.31)>/chromedriver_linux64.zip
unzip chromedriver_linux64.zip -d ~/bin/

### install selnium
#if you type git clone this repository, you do NOT type the command. as below;
pip install selenium

cf. reference
https://qiita.com/shinsaka/items/37436e256c813d277d6d

### create python virtual environment
python -m venv <x: name of virtual environment ex) python version>

### move into python virtual environment
source x/bin/activate

### install all libraries that are needed in order to run this program
pip install -r requirements.txt

## Notes
python --version
Python 3.6.5
Ubuntu 16.04

## If you face trouble...
plz give me comments!
