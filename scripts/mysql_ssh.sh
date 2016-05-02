#!/usr/bin/env bash

cat mysql_slave.sh  | ssh -i EUCA-BUG-OVERFLOW.pem root@64.131.111.26 -o StrictHostKeyChecking=no
sleep 30
ssh -i /team-1-bugoverflow/scripts/EUCA-BUG-OVERFLOW.pem root@64.131.111.27 -o StrictHostKeyChecking=no "yum install git -y"
sleep 30
ssh -i /team-1-bugoverflow/scripts/EUCA-BUG-OVERFLOW.pem root@64.131.111.27 -o StrictHostKeyChecking=no "git clone https://github.com/ITMT-430/team-1-bugoverflow"
ssh -i /team-1-bugoverflow/scripts/EUCA-BUG-OVERFLOW.pem root@64.131.111.27 -o StrictHostKeyChecking=no "/bin/bash /root/team-1-bugoverflow/scripts/mysql_master.sh"

