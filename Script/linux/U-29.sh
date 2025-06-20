export LANG=ko_KR.UTF-8
#!/bin/bash

detail=`cat /etc/xinetd.d/tftp && cat /etc/xinetd.d/talk`
if [ ! -f /etc/xinetd.d/tftp ] && [ ! -f /etc/xinetd.d/talk ]; then
    # tftp, talk 서비스가 비활성화 되어 있는 경우
    echo "서비스 관리,U-29,tftp talk 서비스 비활성화,상,양호,cat /etc/xinetd.d/tftp && cat /etc/xinetd.d/talk의 결과입니다 : $detail,tftp 서비스와 talk 서비스가 비활성화 되어 있는 상태입니다." >> linux_report_$USER.csv
else
    # tftp, talk 서비스가 활성화 되어 있는 경우
    echo -e "서비스 관리,U-29,tftp talk 서비스 비활성화,상,취약,\"cat /etc/xinetd.d/tftp && cat /etc/xinetd.d/talk의 결과입니다 : \n$detail\",tftp 서비스와 talk 서비스가 활성화 되어 있는 상태입니다. 클라우드 취약점 점검 가이드를 참고하시어 /etc/xinetd.d/ 디렉터리 내 tftp, talk, ntalk 파일 내 관련 설정을 주석처리하거나 disable=yes로 설정하여 주시기 바랍니다." >> linux_report_$USER.csv
fi
