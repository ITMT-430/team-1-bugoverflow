#!/bin/bash

# Usage: Run on vagrant machine or another Debian box as root (not sudo - actually switch to root):
# bash <(curl -s https://raw.githubusercontent.com/ITMT-430/Team-3-Install-Scripts/master/deploy-environment.sh)
apt-get install -y git
apt-get install -y vim
apt-get install -y euca2ools
apt-get install -y python-setuptools python-dev libxslt1-dev libxml2 libxml2-dev zlib1g-dev
apt-get remove python-requests
git clone https://github.com/jhajek/euca2ools.git /euca2ools
cd /euca2ools
git checkout origin/maint-3.1
python setup.py install
read -p "Verify there are no errors up to this point, then press any key to continue." nothing
clear
read -p "Copy your credential file to /euca2ools/creds.zip, then press any key to continue." nothing
unzip -d creds creds.zip
source /euca2ools/creds/eucarc
echo "source /euca2ools/creds/eucarc">>~/.bashrc
echo "source /euca2ools/creds/eucarc">>~/.zshrc
echo "Sometimes one of these commands doesn't work right in a script."
echo "If there was an error above, please open a new terminal and type:"
read -p "source /euca2ools/creds/eucarc" nothing
euca-version
outputWS="$(euca-run-instances emi-b6ecd5f1 -n 1 -k 'BugKey' -g 'BugSecurity' -t m1.medium)"
instanceWS="$(echo "${outputWS}" | grep -o 'i-.\{0,8\}' | head -1)"
ipadWS="$(euca-describe-instances | grep ${instanceWS} | grep -o '64\.131\.111\..\{0,3\}' | tr -s [:space:])"
sleep 10
outputDR="$(euca-run-instances emi-b6ecd5f1 -n 1 -k 'BugKey' -g 'BugSQL' -t m1.medium)"
instanceDR="$(echo "${outputDR}" | grep -o 'i-.\{0,8\}' | head -1)"
ipadDR="$(euca-describe-instances | grep ${instanceDW} | grep -o '64\.131\.111\..\{0,3\}' | tr -s [:space:])"
sleep 20
outputDW="$(euca-run-instances emi-b6ecd5f1 -n 1 -k 'BugKey' -g 'BugSQL' -t m1.medium)"
instanceDW="$(echo "${outputDW}" | grep -o 'i-.\{0,8\}' | head -1)"
ipadDW="$(euca-describe-instances | grep ${instanceDW} | grep -o '64\.131\.111\..\{0,3\}' | tr -s [:space:])"

newipWS="$(euca-associate-address -i ${instanceWS} 64.131.111.79)"
newipDR="$(euca-associate-address -i ${instanceDR} 64.131.111.83)"
newipDW="$(euca-associate-address -i ${instanceDW} 64.131.111.84)"

euca-create-tags ${instanceWS} --tag Name=Team1_BugWS
euca-create-tags ${instanceDR} --tag Name=Team1_BugRead
euca-create-tags ${instanceDW} --tag Name=Team1_BugWrite

echo "wait 15 secs"
sleep 15
echo ""
echo "${instanceWS}"
read -p "Please open a new window and ssh into ${newipWS} and verify the connection works." nothing
echo "${instanceDW}"
read -p "Please open a new window and ssh into ${newipDR} and verify the connection works." nothing
echo "${instanceDR}"
read -p "Please open a new window and ssh into ${newipDW} and verify the connection works." nothing

exit
