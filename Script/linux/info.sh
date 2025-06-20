#!/bin/bash

os_version=$(hostnamectl | grep "Operating System" | awk -F ': ' '{print $2}')
ip=$(hostname -I | awk {'print $1'})


echo -e "IP,OS,USER" >> linux_report_$USER.csv
echo -e "$ip,$os_version,$USER" >> linux_report_$USER.csv

