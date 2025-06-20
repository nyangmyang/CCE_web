#!/bin/bash

# /etc/services 파일에 대한 자세한 정보 가져오기
detail=$(ls -l /etc/services)

# 예외처리: /etc/services 파일이 존재하지 않는 경우
if ! [ -e /etc/services ]; then
    echo "파일 및 디렉토리 관리,U-13,/etc/services 파일 및 권한 설정,상,N/A,\"ls -l /etc/services의 결과입니다 : \n/etc/services 파일이 존재하지 않습니다.\",수동 점검이 필요한 항목입니다." >> linux_report_$USER.csv
    exit 1
fi

# /etc/services 파일 검사
owner=$(stat -c "%U" /etc/services)  # 파일 소유자 확인
permission=$(stat -c "%a" /etc/services)  # 파일 권한 확인

# 소유자가 root이고 권한이 644 이하인지 확인
if [ "$owner" == "root" ] && [ "$permission" -le 644 ]; then
    echo -e "파일 및 디렉토리 관리,U-13,/etc/services 파일 및 권한 설정,상,양호,\"ls -l /etc/services의 결과입니다 : \n$detail\",/etc/services 파일의 소유자가 root이고 권한이 644 이하인 상태입니다." >> linux_report_$USER.csv
else
    echo -e "파일 및 디렉토리 관리,U-13,/etc/services 파일 및 권한 설정,상,취약,\"ls -l /etc/services의 결과입니다 : \n$detail\",/etc/services 파일의 소유자가 root가 아니거나 권한이 644 초과인 상태입니다. 클라우드 취약점 점검 가이드를 참고하시어 \"/etc/services\" 파일의 소유자를 root로 변경하시고 권한을 644(-rw-r--r--)로 설정하여 주시기 바랍니다." >> linux_report_$USER.csv
fi
