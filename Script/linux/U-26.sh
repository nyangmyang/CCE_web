#!/bin/bash
export LANG=ko_KR.UTF-8

detail=`ps -ef | grep automount >/dev/null 2>&1`
# automountd 서비스 데몬 확인

if [ -z "$detail" ] ; then
	# automount 서비스가 비활성화 되어 있는 경우
	echo "서비스 관리,U-26,automountd 제거,상,양호,ps -ef | grep automount >/dev/null 2>&1의 결과입니다 : $detail,automount 서비스가 비활성화 되어 있는 상태입니다.">> linux_report_$USER.csv
else
	# automount 서비스가 활성화되어 있는 경우
	echo "서비스 관리,U-26,automountd 제거,상,취약,ps -ef | grep automount >/dev/null 2>&1의 결과입니다 : $detail,automount 서비스가 활성화 되어 있는 상태입니다. 클라우드 취약점 점검 가이드를 참고하시어 automound 서비스 데몬을 중지시켜 주시고 시스템 재시작 시 automount가 시작되지 않도록 설정하여 주시기 바랍니다.">> linux_report_$USER.csv
fi