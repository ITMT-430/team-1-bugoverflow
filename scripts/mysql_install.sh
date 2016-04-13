#!/usr/bin/env bash
​
# I'm using && so the the commands stop continuing if any command fails
yum install -y mysql-server mysql &&         # install sql
service mysqld start &&
mysqladmin -u root password leech &&      # root:leech user created
chkconfig mysqld on &&             # set to start on boot
​
# in final build, the user should be
# "reader"@"64.131.111.32"
# to limit the allowed IPs for remote connections to only the webserver. 
​
# create the reader user, remote login allowed by default
echo "create user 'master' identified by 'leech'" | mysql -u root -pleech;
