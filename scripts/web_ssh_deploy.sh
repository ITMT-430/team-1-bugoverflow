#!/usr/bin/env bash

cat web_deploy.sh | ssh -i EUCA-BUG-OVERFLOW.pem root@64.131.111.33 -o StrictHostKeyChecking=no
