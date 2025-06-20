#!/bin/bash

ps -ef | grep nfsd | grep -v grep > /dev/null 2>&1
psef=`ps -ef | grep nfsd | grep -v grep`


if [ $? -eq 0 ]; then
	echo "서비스 관리,U-24,NFS 서비스 비활성화,상,취약,\"ps -ef | grep nfsd | grep -v grep의 결과입니다 :  $psef\",NFS 관련 데몬이 활성화되어 있습니다. 클라우드 취약점 점검 가이드를 참고하시어 NFS 데몬(nfsd)을 중지하여 주시기 바랍니다." >> ./result/linux_report_$USER.csv
else
	echo "서비스 관리,U-24,NFS 서비스 비활성화,상,양호,\"ps -ef | grep nfsd | grep -v grep의 결과입니다 :  $psef\",NFS 관련 데몬이 비활성화되어 있습니다." >> linux_report_$USER.csv
fi
