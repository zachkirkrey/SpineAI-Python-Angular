#!/bin/sh

cd "$(dirname "$0")"

if [ ! -d ./venv ]
then
  python3.7 -m venv venv
fi

./venv/bin/python -m pip install pip --upgrade
./venv/bin/python -m pip install wheel
./venv/bin/python -m pip install -r requirements.txt

sudo apt install fontconfig libxrender1 xfonts-75dpi xfonts-base
sudo apt --fix-broken install
wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.bionic_amd64.deb -O /tmp/wkhtmltopdf.deb
sudo dpkg -i /tmp/wkhtmltopdf.deb
