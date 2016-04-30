#!/usr/bin/env bash

SCRIPTPATH=$( cd $(dirname $0) ; pwd -P )
cd $SCRIPTPATH

if [ ! -s EUCA-BUG-OVERFLOW.pem ]; then
    echo "You need to decrypt the pem key first, so I can ssh to the servers" &&
        exit 0;
fi

/bin/bash mysql_ssh.sh
/bin/bash web_ssh_deploy.sh

