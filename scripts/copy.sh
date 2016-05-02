#!/bin/bash

gpg -o /team-1-bugoverflow/scripts/EUCA-BUG-OVERFLOW.pem -d /team-1-bugoverflow/scripts/EUCA-BUG-OVERFLOW.pem.gpg
chmod 400 /team-1-bugoverflow/scripts/EUCA-BUG-OVERFLOW.pem
scp -oStrictHostKeyChecking=no -i /team-1-bugoverflow/scripts/EUCA-BUG-OVERFLOW.pem /team-1-bugoverflow/scripts/EUCA-BUG-OVERFLOW.pem root@64.131.111.27:/root/EUCA-BUG-OVERFLOW.pem
scp -oStrictHostKeyChecking=no -i /team-1-bugoverflow/scripts/EUCA-BUG-OVERFLOW.pem /team-1-bugoverflow/Log/server/rsyslog.conf root@64.131.111.30:/etc/rsyslog.conf
scp -oStrictHostKeyChecking=no -i /team-1-bugoverflow/scripts/EUCA-BUG-OVERFLOW.pem /team-1-bugoverflow/Log/client/rsyslog.conf root@64.131.111.26:/etc/rsyslog.conf
scp -oStrictHostKeyChecking=no -i /team-1-bugoverflow/scripts/EUCA-BUG-OVERFLOW.pem /team-1-bugoverflow/Log/client/rsyslog.conf root@64.131.111.27:/etc/rsyslog.conf
scp -oStrictHostKeyChecking=no -i /team-1-bugoverflow/scripts/EUCA-BUG-OVERFLOW.pem /team-1-bugoverflow/Log/client/rsyslog.conf root@64.131.111.32:/etc/rsyslog.conf
ssh root@64.131.111.30 'bash -s' < /team-1-bugoverflow/scripts/logger.sh