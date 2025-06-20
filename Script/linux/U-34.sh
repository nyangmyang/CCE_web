#!/bin/bash

FILE=/etc/named.conf

# DNS 서비스 확인
if [ $(ps -ef | grep named | grep -v grep | wc -l) -eq 0 ]; then
	# DNS 서비스 미사용
	result="양호"
	detail="DNS 서비스를 사용하지 않는 상태입니다."
	command=$(ps -ef | grep named | grep -v grep | wc -l)
	comment="ps -ef | grep named | grep -v grep | wc -l의 결과값입니다 : "
else
	# DNS 서버 사용
	# 파일 유무/허용범위 확인
	if [ -f $FILE ] ; then
		cat $FILE | grep 'allow-transfer' >/dev/null	#허용범위 확인
		if [ $? == 0 ] ; then
			result="양호"
			detail= "DNS 서비스를 사용하며 Zone Transfer를 허가된 사용자에게만 허용한 상태입니다."
			command=$(cat $FILE | grep 'allow-transfer' >/dev/null)
		else
			result="취약"
			detail="DNS 서비스를 사용하며 Zone Transfer를 모든 사용자에게 허용한 상태입니다. 클라우드 취약점 점검 가이드를 참고하시어 \"/etc/named.conf\" 파일의 \"Options\"를 특정 서버의 Zone Tranfer로 지정하여 주시기 바랍니다."
		fi
	else
		result="취약"
	fi
fi

echo "서비스 관리,U-34,DNS ZoneTransfer 설정,상,$result,$comment $command,$detail" >> linux_report_$USER.csv
