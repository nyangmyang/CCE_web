#!/bin/bash

# /etc/shadow 파일이 있는지 확인
# 파일이 없는 경우 기록 후 스크립트 종료
if [ ! -f /etc/shadow ]; then
  echo "/etc/shadow file not found. Vulnerable" >> linux_report_$USER.csv
  exit 1
fi

# /etc/shadow 파일의 권한 정보를 detail1 변수에 저장
detail1=`ls -l /etc/shadow | tr '\n' ' ' | tr '\r' ' '`
# /etc/passwd 파일의 내용을 detail2 변수에 저장
detail2=`cat /etc/passwd | tr '\n' ' ' | tr '\r' ' '`

# /etc/passwd 파일의 두 번째 필드에 "x"가 있는지 확인
# 실제 패스워드 정보는 /etc/shadow 파일에 저장, "x"일 경우, 분리해놓은 것으로 양호로 판단
if grep -q "^[^:]*:[x!]" /etc/passwd; then
  echo -e "계정관리,U-05,패스워드 파일 보호,상,양호,\"ls -l /etc/shadow의 결과입니다 :\n$detail1 \ncat /etc/passwd의 결과입니다 : \n$detail2\",쉐도우 패스워드를 사용하거나 패스워드를 암호화하여 저장하고 있습니다." >> linux_report_$USER.csv
else
  echo -e "계정관리,U-05,패스워드 파일 보호,상,취약,\"ls -l /etc/shadow의 결과입니다 :\n$detail1 \ncat /etc/passwd의 결과입니다 : \n$detail2\",쉐도우 패스워드를 사용하지 않고 패스워드를 암호화하여 저장하지 않고 있습니다. 클라우드 취약점 점검 가이드를 참고하시어 쉐도우 패스워드 정책을 적용하시거나 일반 패스워드 정책을 적용하시기 바랍니다." >> linux_report_$USER.csv
fi

#ok2(다시)
