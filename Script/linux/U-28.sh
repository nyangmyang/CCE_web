#!/bin/bash
export LANG=ko_KR.UTF-8

detail=`ps -ef | egrep “ypserv|ypbind|ypxfrd|rpc.yppasswdd|rpc.ypupdated” | grep -v "grep"`
# ypserv, ypbind, ypxfrd, rpc.yppasswdd, rpc.ypupdated가 실행 중인지 확인
if ps -ef | egrep "ypserv|ypbind|ypxfrd|rpc.yppasswdd|rpc.ypupdated" | grep -v "grep" > /dev/null; then
    # NIS, NIS+ 서비스가 구동 중일 경우
    echo "서비스 관리,U-28,NIS NIS+ 점검,상,취약,ps -ef | egrep “ypserv|ypbind|ypxfrd|rpc.yppasswdd|rpc.ypupdated” | grep -v "grep"의 결과입니다 : $detail,NIS또는 NIS+ 서비스가 구동 중인 상태입니다. 클라우드 취약점 점검 가이드를 참고하시어 NFS 서비스 데몬을 중지하여 주시기 바랍니다." >> linux_report_$USER.csv
else
    # NIS, NIS+ 서비스가 구동 중이지 않을 경우
    echo "서비스 관리,U-28,NIS NIS+ 점검,상,양호,ps -ef | egrep “ypserv|ypbind|ypxfrd|rpc.yppasswdd|rpc.ypupdated” | grep -v "grep"의 결과입니다 : $detail,NIS또는 NIS+ 서비스가 구동 중이지 않은 상태입니다." >> linux_report_$USER.csv
fi
