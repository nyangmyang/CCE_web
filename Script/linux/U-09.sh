#!/bin/bash

CODE="U-09"
VULN=false

detail=$(ls -l /etc/shadow)

# /etc/shadow가 없는 경우 비정상 종료
if [[ ! -e "/etc/shadow" ]]; then
    echo "[$CODE] N/A: /etc/shadow does not exist."
    if [ -e "linux_report_$USER.csv" ]; then
        echo "파일 및 디렉토리 관리,$CODE,/etc/shadow 파일 소유자 및 권한 설정,상,N/A,/etc/shadow 파일이 존재하지 않습니다.,수동 점검이 필요한 항목입니다." >> linux_report_$USER.csv
        echo "[$CODE] Report generated."
    else
        echo "구분,진단 코드,진단 항목,취약도,점검 결과,시스템 실제 결과값,상세설명 및 조치방안" > linux_report_$USER.csv
        echo "파일 및 디렉토리 관리,$CODE,/etc/shadow 파일 소유자 및 권한 설정,상,N/A,/etc/shadow 파일이 존재하지 않습니다.,수동 점검이 필요한 항목입니다." >> linux_report_$USER.csv
        echo "[$CODE] Report generated."
    fi
    exit 1
fi

# /etc/shadow 파일의 소유자가 root인지 확인
if [ "$(stat -c '%U' /etc/shadow)" != "root" ]; then
    echo "[$CODE] VULN: The owner of /etc/shadow is not root."
    VULN=true
fi

# /etc/shadow 파일의 권한이 400 이하인지 확인
if [ "$(stat -c '%a' /etc/shadow)" -gt 400 ]; then
    echo "[$CODE] VULN: The permissions of /etc/shadow are not 400 or less."
    VULN=true
fi

# 취약점이 발견되지 않았을 경우 메시지 출력
if [ "$VULN" = false ]; then
    echo "[$CODE] OK: No vulnerability found"
fi

# VULN 값에 따라 취약 / 양호 레포트 작성.
if [ "$VULN" = true ]; then
    REPORT="파일 및 디렉토리 관리,$CODE,/etc/shadow 파일 소유자 및 권한 설정,상,취약, \"ls -l /etc/shadow의 결과입니다 : $detail\",/etc/shadow 파일의 소유자가 root가 아니거나 권한이 400초과인 상태입니다. 클라우드 취약점 점검 가이드를 참고하시어 /etc/shadow 파일의 소유자를 root로 변경하시고 권한을 400(-r--------)로 설정하여 주시기 바랍니다."
else
    REPORT="파일 및 디렉토리 관리,$CODE,/etc/shadow 파일 소유자 및 권한 설정,상,양호, \"ls -l /etc/shadow의 결과입니다 : $detail\",/etc/shadow 파일의 소유자가 root이고 권한이 400이하인 상태입니다."
fi

# 파일이 존재하면 이어서 작성, 존재하지 않으면 보고서 헤더 작성 후 레포트 작성.
if [ -e "linux_report_$USER.csv" ]; then
    echo -e "$REPORT" >> linux_report_$USER.csv
    echo "[$CODE] Report generated."
else
    echo "구분,진단 코드,진단 항목,취약도,점검 결과,시스템 실제 결과값,상세설명 및 조치방안" > linux_report_$USER.csv
    echo -e "$REPORT" >> linux_report_$USER.csv
    echo "[$CODE] Report generated."
fi

exit 0
# check
