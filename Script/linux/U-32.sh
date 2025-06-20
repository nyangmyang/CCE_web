#!/bin/bash

# SMTP 확인
if ps -ef | grep -v grep | grep -q sendmail; then
    # SMTP 서비스 사용
    if cat /etc/mail/sendmail.cf | grep -q "restrictqrun"; then
        # 실행 방지 적용
        result="양호"
		  detail="SMTP 서비스를 사용 중이며, restrictqrun 옵션이 설정되어 Sendmail 실행 방지가 설정되어 있는 상태입니다."
		  command=$(cat /etc/mail/sendmail.cf | grep -q "restrictqrun")
		  comment="cat /etc/mail/sendmail.cf | grep -q \"restrictqrun\"의 결과값입니다 : "
    else
        # 실행 방지 미적용
        result="취약"
		  detail="SMTP 서비스를 사용 중이며, restrictqrun 옵션이 설정되어 있이 않아 Sendmail 실행 방지가 설정되어 있지 않은 상태입니다. 클라우드 취약점 점검 가이드를 참고하시어 \"/etc/mail/sendmail.cf\" 파일을 연 후 \"O PrivacyOptions=\" 설정 부분에 restrictqrun 옵션을 추가해주시기 바랍니다."
		  command=$(cat /etc/mail/sendmail.cf | grep -q "restrictqrun")
		  comment="cat /etc/mail/sendmail.cf | grep -q \"restrictqrun\"의 결과값입니다 : "
    fi
else
    # SMTP 서비스 미사용
    result="양호"
    detail="SMTP 서비스를 사용하지 않는 상태입니다."
    command=$(ps -ef | grep -v grep | grep -q sendmail)
    comment="ps -ef | grep -v grep | grep -q sendmail의 결과값입니다 : "
fi

echo "서비스 관리,U-32,일반사용자의 Sendmail 실행 방지,상,$result,$comment $command,$detail" >> linux_report_$USER.csv
