#!/bin/bash

iptables -A INPUT -m state --state NEW -m udp -p udp --dport 514 -j ACCEPT
service rsyslog restart