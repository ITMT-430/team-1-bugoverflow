#!/bin/bash
yum install vim git epel-release python-pip python-devel gcc nginx python mysql mysql-server -y
yum install wget -y
yum install xinetd -y
yum install rpcbind -y
service nginx start
chkconfig nginx on
pip install virtualenv
cd ..
git clone https://github.com/ITMT-430/team-1-bugoverflow

yum remove python
wget http://www.python.org/ftp/python/2.7.6/Python-2.7.6.tar.xz
yum install xz-libs -y
xz -d Python-2.7.6.tar.xz
tar -xvf Python-2.7.6.tar
cd Python-2.7.6
./configure --prefix=/usr/local    
make
make altinstall
service xinetd restart
service rpcbind restart
service rsyslog restart

cd /team-1-bugoverflow/flask/

virtualenv flaskenv
source flaskenv/bin/activate
pip install uwsgi
pip install flask
pip install Jinja2
pip install Flask-SQLAlchemy
pip install exifread
pip install pymysql
pip install flask_recaptcha
pip install requests
#pip install Flask-AlchemyDumps
#Flask-AlchemyDumps require python 2.7+
yum install python-jinja2 -y
#cd /team-1-bugoverflow/flask && source flaskenv/bin/activate && 
python -c "import mydb; mydb.rebuilddb()"

rm -f /etc/nginx/nginx.conf
mv /team-1-bugoverflow/flask/nginx.conf /etc/nginx/nginx.conf
service nginx restart
chmod 655 test.conf
mv test.conf /etc/init/test.conf

/etc/init/test.conf start
