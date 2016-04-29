#!/bin/bash

git clone https://github.com/ITMT-430/team-1-bugoverflow /team-1-bugoverflow
gpg --passphrase leech -o /root/EUCA-BUG-OVERFLOW.pem -d /team-1-bugoverflow/scripts/EUCA-BUG-OVERFLOW.pem.gpg
chmod 400 /root/EUCA-BUG-OVERFLOW.pem
scp -oStrictHostKeyChecking=no -i EUCA-BUG-OVERFLOW.pem /root/EUCA-BUG-OVERFLOW.pem root@64.131.111.80:/root/EUCA-BUG-OVERFLOW.pem
