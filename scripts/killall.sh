#!/bin/bash
euca-disassociate-address 64.131.111.26
euca-disassociate-address 64.131.111.27
euca-disassociate-address 64.131.111.32
open="$(euca-describe-instances | grep Team1_Bug | awk '{print $3}')"
euca-terminate-instances ${open}
rm /euca2ools/ -R
rm "/team-1-bugoverflow/" -R
