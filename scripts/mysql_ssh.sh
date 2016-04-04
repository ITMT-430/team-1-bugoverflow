#!/usr/bin/env bash
​
cat mysql_remove.sh  | ssh -i EUCA-BUG-OVERFLOW.pem root@64.131.111.27
cat mysql_install.sh | ssh -i EUCA-BUG-OVERFLOW.pem root@64.131.111.27
