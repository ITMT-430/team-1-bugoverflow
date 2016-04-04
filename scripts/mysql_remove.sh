#!/usr/bin/env bash
yum remove -y mysql-server mysql; # remove the software
rm -rf /var/lib/mysql/;        # remove the data