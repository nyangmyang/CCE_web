#!/bin/bash

# SMTP 사용여부
if ps -ef | grep sendmail | grep -v "grep" > /dev/null; then
    # SMTP 사용할때 릴레이 제한 설정 확인
    if cat /etc/mail/sendmail.cf | grep "R$ \*" | grep "Relaying denied" > /dev/null; then
        # 릴레이 제한 설정 O
        result="양호"
	detail=`ps -ef | grep sendmail | grep -v "grep" > /dev/null`
	echo "서비스 관리,U-31,스팸 메일 릴레이 제한,상,$result,ps -ef | grep sendmail | grep -v "grep" > /dev/null의 결과입니다 :$detail, SMTP서비스를 사용하고 있지만 릴레이 제한이 설정되어 있습니다. " >> linux_report_$USER.csv
    else
        # 릴레이 제한 설정 X
        result="취약"
	echo "서비스 관리,U-31,스팸 메일 릴레이 제한,상,$result,ps -ef | grep sendmail | grep -v "grep" > /dev/null의 결과입니다 :$detail,SMTP서비스를 사용하며 릴레이 제한이 설정되어 있지 않습니다. 클라우드 취약점 점검 가이드를 참고하시어 sendmail.cf 설정파일 내 관련 설정의 주석을 제거하시고 특정 IP, domain, Email Address 및 네트워크에 대한 sendmail 접근 제한을 확인하여 주시기 바랍니다." >> linux_report_$USER.csv
    fi
else
    # SMTP 미사용
    result="양호"
	echo "서비스 관리,U-31,스팸 메일 릴레이 제한,상,$result,ps -ef | grep sendmail | grep -v "grep" > /dev/null의 결과입니다 : $detail,SMTP 서비스를 사용하지 않는 상태입니다." >> linux_report_$USER.csv
fi

# 저장


