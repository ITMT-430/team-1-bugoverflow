#!/usr/bin/env bash
​
cat mysql_slave.sh  | ssh -i EUCA-BUG-OVERFLOW.pem root@64.131.111.26 -o StrictHostKeyChecking=no
sleep 60
cat mysql_master.sh | ssh -i EUCA-BUG-OVERFLOW.pem root@64.131.111.27 -o StrictHostKeyChecking=no

