#!/bin/bash

# Usage: Run on vagrant machine or another Debian box as root (not sudo - actually switch to root):
# bash <(curl -s https://raw.githubusercontent.com/ITMT-430/Team-3-Install-Scripts/master/deploy-environment.sh)
apt-get install -y git vim eucatools
apt-get install -y python-setuptools python-dev libxslt1-dev libxml2 libxml2-dev zlib1g-dev
apt-get remove -y python-requests
git clone https://github.com/jhajek/euca2ools.git /euca2ools
git clone https://github.com/ITMT-430/team-1-bugoverflow /team-1-bugoverflow
cd /team-1-bugoverflow
git pull origin master
cd /euca2ools
git checkout origin/maint-3.1
python setup.py install
read -p "Verify there are no errors up to this point, then press any key to continue." nothing
clear
gpg -o /euca2ools/creds.zip -d /team-1-bugoverflow/scripts/creds.zip.gpg
unzip -d creds creds.zip
source /euca2ools/creds/eucarc
echo "source /euca2ools/creds/eucarc">>~/.bashrc
echo "source /euca2ools/creds/eucarc">>~/.zshrc

euca-version
echo "Deploying instances now, please wait."
outputWS="$(euca-run-instances emi-b6ecd5f1 -n 1 -k 'BugKey' -g 'BugSecurity' -t m1.xlarge)"
instanceWS="$(echo "${outputWS}" | grep -o 'i-.\{0,8\}' | head -1)"
ipadWS="$(euca-describe-instances | grep ${instanceWS} | grep -o '64\.131\.111\..\{0,3\}' | tr -s [:space:])"
sleep 25

outputDR="$(euca-run-instances emi-b6ecd5f1 -n 1 -k 'BugKey' -g 'BugSQL' -t m1.xlarge)"
instanceDR="$(echo "${outputDR}" | grep -o 'i-.\{0,8\}' | head -1)"
ipadDR="$(euca-describe-instances | grep ${instanceDR} | grep -o '64\.131\.111\..\{0,3\}' | tr -s [:space:])"
sleep 25

outputDW="$(euca-run-instances emi-b6ecd5f1 -n 1 -k 'BugKey' -g 'BugSQL' -t m1.xlarge)"
instanceDW="$(echo "${outputDW}" | grep -o 'i-.\{0,8\}' | head -1)"
ipadDW="$(euca-describe-instances | grep ${instanceDW} | grep -o '64\.131\.111\..\{0,3\}' | tr -s [:space:])"
sleep 25

outputL="$(euca-run-instances emi-b6ecd5f1 -n 1 -k 'BugKey' -g 'BugSecurity' -t m1.xlarge)"
instanceL="$(echo "${outputL}" | grep -o 'i-.\{0,8\}' | head -1)"
ipadL="$(euca-describe-instances | grep ${instanceL} | grep -o '64\.131\.111\..\{0,3\}' | tr -s [:space:])"
sleep 25


echo "wait 10 secs, IPs are being added"
sleep 1
newipWS="$(euca-associate-address -i ${instanceWS} 64.131.111.32)"
echo ${newipWS}
sleep 3
newipDR="$(euca-associate-address -i ${instanceDR} 64.131.111.26)"
echo ${newipDR}
sleep 3
newipDW="$(euca-associate-address -i ${instanceDW} 64.131.111.27)"
echo ${newipDW}
sleep 3
newipL="$(euca-associate-address -i ${instanceL} 64.131.111.30)"
echo ${newipL}
sleep 3

echo "wait 10 secs, Servers are being named"
sleep 1
euca-create-tags ${instanceWS} --tag Name=Team1_BugWS
sleep 3
euca-create-tags ${instanceDR} --tag Name=Team1_BugRead
sleep 3
euca-create-tags ${instanceDW} --tag Name=Team1_BugWrite
sleep 3
euca-create-tags ${instanceL} --tag Name=Team1_BugLog
sleep 3

echo "Instances should be up and running now, check the Eucalyptus web page. Running the next script soon."

sleep 20
ssh-keygen -f "/root/.ssh/known_hosts" -R 64.131.111.26
ssh-keygen -f "/root/.ssh/known_hosts" -R 64.131.111.27
ssh-keygen -f "/root/.ssh/known_hosts" -R 64.131.111.32
ssh-keygen -f "/root/.ssh/known_hosts" -R 64.131.111.30


/bin/bash /team-1-bugoverflow/scripts/copy.sh
/bin/bash /team-1-bugoverflow/scripts/grand_deploy.sh

exit
