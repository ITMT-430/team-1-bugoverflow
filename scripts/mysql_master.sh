#!/usr/bin/env bash
yum install vim mysql-server -y    		 #Install msql clients/server and git
yum install xinetd -y
yum install rpcbind -y
#cd ..							 
#git clone https://github.com/ITMT-430/team-1-bugoverflow #Pull repo
rm -f /etc/my.cnf					 #Removes SQL config
touch /var/lib/mysql/mysql-bin.log
cp /root/team-1-bugoverflow/Nginx/Master.cnf /etc/my.cnf      #Replace SQL config
mkdir /var/log/mysql					 #Creates log file
chown -R mysql:mysql /var/log/mysql			 #Grant SQL access log file
service mysqld start					 #Start SQL
service xinetd restart
service rpcbind restart
service rsyslog restart




mysqladmin -u root password leech	      		 # root:leech user created
chkconfig mysqld on            				 # set to start on boot


#SQL Configuration
mysql -u root -pleech -e "CREATE USER 'master'@'64.131.111.32' IDENTIFIED BY 'leech';"
mysql -u root -pleech -e "GRANT ALL PRIVILEGES ON * . * TO 'master'@'64.131.111.32' IDENTIFIED BY 'leech';"
mysql -u root -pleech -e "GRANT ALL PRIVILEGES ON * . * TO 'master'@'localhost' IDENTIFIED BY 'leech';"
mysql -u root -pleech -e "FLUSH PRIVILEGES;"
mysql -u root -pleech -e "CREATE DATABASE newdatabase;"
mysql -u root -pleech -e "GRANT REPLICATION SLAVE ON *.* TO 'root'@'64.131.111.95' IDENTIFIED BY 'leech';"
mysql -u root -pleech -e "FLUSH PRIVILEGES;"
mysql -u root -pleech -e "USE newdatabase;"
mysql -u root -pleech -e "FLUSH TABLES WITH READ LOCK;"
a=$(mysql -u root -pleech -e "SHOW MASTER STATUS" | sed -n 2p | awk '{print $1}')
b=$(mysql -u root -pleech -e "SHOW MASTER STATUS" | sed -n 2p | awk '{print $2}')
mysql -u root -pleech -e "UNLOCK TABLES;"

chmod 400 /root/EUCA-BUG-OVERFLOW.pem
c='ssh -i /root/EUCA-BUG-OVERFLOW.pem root@64.131.111.95 -o StrictHostKeyChecking=no "mysql -u root -pleech -e \"CHANGE MASTER TO MASTER_HOST='"'64.131.111.93'"',MASTER_USER='"'root'"', MASTER_PASSWORD='"'leech'"', MASTER_LOG_FILE='"'$a'"', MASTER_LOG_POS='$b';\""'

ssh -i /root/EUCA-BUG-OVERFLOW.pem root@64.131.111.95 -o StrictHostKeyChecking=no "mysql -u root -pleech -e \"STOP SLAVE;\""
ssh -i /root/EUCA-BUG-OVERFLOW.pem root@64.131.111.95 -o StrictHostKeyChecking=no "mysql -u root -pleech -e \"RESET SLAVE;\""
eval $c
ssh -i /root/EUCA-BUG-OVERFLOW.pem root@64.131.111.95 -o StrictHostKeyChecking=no "mysql -u root -pleech -e \"START SLAVE;\""

