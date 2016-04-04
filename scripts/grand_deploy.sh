#!/usr/bin/env bash

if [ ! -s EUCA-BUG-OVERFLOW.pem ]; then
    echo "You need to decrypt the pem key first, so I can ssh to the servers" &&
        exit 0;
fi

web_ssh_deploy.sh
mysql_ssh.sh
