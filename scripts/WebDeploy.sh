#!/bin/bash
sudo yum install vim git -y
sudo yum install epel-release -y
sudo yum install python-pip python-devel gcc nginx python -y
sudo service nginx start
sudo chkconfig nginx on
sudo pip install virtualenv
cd ..
git clone https://github.com/ITMT-430/team-1-bugoverflow

sudo yum remove python
wget http://www.python.org/ftp/python/2.7.6/Python-2.7.6.tar.xz
yum install xz-libs -y
xz -d Python-2.7.6.tar.xz
tar -xvf Python-2.7.6.tar
cd Python-2.7.6
./configure --prefix=/usr/local    
make
make altinstall

cd team-1-bugoverflow/flask/

virtualenv flaskenv
source flaskenv/bin/activate
pip install uwsgi flask Jinja2
yum install python-jinja2 -y

python test.py