#!/usr/bin/env bash
yum install git mysql-server -y    		 #Install msql clients/server and git
yum install xinetd -y
yum install rpcbind -y
cd ..							 
git clone https://github.com/ITMT-430/team-1-bugoverflow #Pull repo
rm -f /etc/my.cnf					 #Removes SQL config
cp /team-1-bugoverflow/Nginx/Slave.cnf /etc/my.cnf       #Replace SQL config
touch /var/lib/mysql/mysql-bin.log
#mkdir /var/log/mysql					 #Creates log file
#chown -R mysql:mysql /var/log/mysql			 #Grant SQL access log file
service mysqld start					 #Start SQL
service xinetd restart
service rpcbind restart
service rsyslog restart

mysqladmin -u root password leech	      		 # root:leech user created
chkconfig mysqld on            				 # set to start on boot

#SQl Configuration
mysql -u root -pleech -e "CREATE USER 'slave'@'64.131.111.33' IDENTIFIED BY 'leech';"
mysql -u root -pleech -e "GRANT ALL PRIVILEGES ON * . * TO 'slave'@'64.131.111.33' IDENTIFIED BY 'leech';"
mysql -u root -pleech -e "GRANT ALL PRIVILEGES ON * . * TO 'slave'@'localhost' IDENTIFIED BY 'leech';"
mysql -u root -pleech -e "FLUSH PRIVILEGES;"
mysql -u root -pleech -e "CREATE DATABASE newdatabase;"

