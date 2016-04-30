#!/usr/bin/env bash
sudo yum install git mysql-server -y    		 #Install msql clients/server and git
cd ..							 
git clone https://github.com/ITMT-430/team-1-bugoverflow #Pull repo
rm -f /etc/my.cnf					 #Removes SQL config
cp /team-1-bugoverflow/Nginx/Slave.cnf /etc/my.cnf       #Replace SQL config
mkdir /var/log/mysql					 #Creates log file
chown -R mysql:mysql /var/log/mysql			 #Grant SQL access log file
service mysqld start					 #Start SQL

mysqladmin -u root password leech	      		 # root:leech user created
chkconfig mysqld on            				 # set to start on boot

