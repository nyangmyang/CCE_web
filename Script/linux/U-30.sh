#!/bin/bash
export LANG=ko_KR.UTF-8

# Sendmail 프로세스 확인
sendmail_process=$(ps -ef | grep -v grep | grep sendmail)

# Postfix 프로세스 확인
postfix_process=$(systemctl status postfix)

# Sendmail과 Postfix 둘 다 사용하지 않는 경우 N/A 처리
if [ -z "$sendmail_process" ] && [ "$postfix_process" != "active" ]; then
    printf "서비스 관리,U-30,Sendmail 버전 점검,상,N/A,\"ps -ef | grep -v grep | grep sendmail의 결과입니다 : %s\nsystemctl status postfix의 결과입니다. : %s\",\"Sendmail과 Postfix가 사용되고 있지 않습니다.\"\n" "$sendmail_process" "$postfix_process" >> linux_report_$USER.csv
    exit 0
fi

# Sendmail 사용 시 버전 확인
if [ ! -z "$sendmail_process" ]; then
    if [ -e "/etc/mail/sendmail.cf" ]; then
        sendmail_version=$(grep DZ /etc/mail/sendmail.cf | awk '{print $2}')
        echo -e "서비스 관리,U-30,Sendmail 버전 점검,상,인터뷰,\"cat /etc/mail/sendmail.cf | grep DZ의 결과입니다 : $sendmail_version\",\"Sendmail 현재 버전: $sendmail_version.\n담당자와 인터뷰를 통해 최신 버전으로 업데이트하십시오.\"" >> linux_report_$USER.csv
    else
        echo -e "서비스 관리,U-30,Sendmail 버전 점검,상,인터뷰,\"Sendmail 서비스가 실행 중이나, /etc/mail/sendmail.cf 파일이 없습니다.\",\"Sendmail 설치 및 구성을 확인하십시오.\"" >> linux_report_$USER.csv
    fi
fi

# Postfix 사용 시 버전 확인
if [ "$postfix_process" == "active" ]; then
    postfix_version=$(postconf -d | grep mail_version | awk '{print $3}')
    echo -e "서비스 관리,U-30,Postfix 버전 점검,상,인터뷰,\"postconf -d | grep mail_version의 결과입니다 : $postfix_version\",\"Postfix 현재 버전: $postfix_version.\n담당자와 인터뷰를 통해 최신 버전으로 업데이트하십시오.\"" >> linux_report_$USER.csv
fi

