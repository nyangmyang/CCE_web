#!/bin/bash

CODE="U-07"
VULN=false

# 소유자나 그룹이 없는 파일 및 디렉터리 검색
search_result=$(find / -nouser -o -nogroup 2> /dev/null)

# 검색 결과 출력
if [ -z "$search_result" ]; then
    echo "[$CODE] OK: No files or directories without owners or groups found."
else
    echo "[$CODE] VULN: Files or directories without owners or groups:"
    echo "$search_result"
    VULN=true
fi

detail1=$(find / -nouser -o -nogroup 2> /dev/null)
detail2=$(find /etc /tmp /bin /sbin \( -nouser -o -nogroup \) -xdev -exec ls -al {} \; 2> /dev/null)
good='소유자나 그룹이 존재하지 않는 파일 및 디렉터리가 없습니다.'
bad='소유자나 그룹이 존재하지 않는 파일 및 디렉터리가 있습니다. 클라우드 취약점 점검 가이드를 참고하시어 소유자가 존재하지 않는 파일이나 디렉터리가불필요한 경우 rm명령으로 삭제하시고 필요한 경우 chown 명령으로 소유자 및 그룹을 변경하여 주시기 바랍니다.'

# VULN 값에 따라 취약 / 양호 레포트 작성.
if [ "$VULN" = true ]; then
    REPORT="파일 및 디렉토리 관리,$CODE,파일 및 디렉터리 소유자 설정,상,취약,\"find / -nouser -o -nogroup의 결과입니다 : $detail1\nfind /etc /tmp /bin /sbin \( -nouser -o -nogroup \) -xdev -exec ls -al {} \; 2> /dev/null의 결과입니다 : \n$detail2\",$bad"
else
    REPORT="파일 및 디렉토리 관리,$CODE,파일 및 디렉터리 소유자 설정,상,양호,\"find / -nouser -o -nogroup의 결과입니다 : 없음\n$detail1\nfind /etc /tmp /bin /sbin \( -nouser -o -nogroup \) -xdev -exec ls -al {} \; 2> /dev/null의 결과입니다 : $detail2\",$good"
fi

# 파일이 존재하면 이어서 작성, 존재하지 않으면 보고서 헤더 작성 후 레포트 작성.
if [ -e "linux_report_$USER.csv" ]; then
    echo -e "$REPORT" >> linux_report_$USER.csv
    echo "[$CODE] Report generated."
else
    echo "구분,진단 코드,진단 항목,취약도,점검 결과,시스템 실제 결과값,상세설명" > linux_report_$USER.csv
    echo -e "$REPORT" >> linux_report_$USER.csv
    echo "[$CODE] Report generated."
fi

exit 0
# ok2