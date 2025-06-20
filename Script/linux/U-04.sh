#!/bin/bash

# /etc/login.defs 파일에서 패스워드 최대 사용 기간의 설정 값을 확인
# PASS_MAX_DAYS 값에 해당하는 라인을 찾아서 awk 이용하여 값 추출 후 password_max_age 변수에 저장
password_max_age=$(grep "^PASS_MAX_DAYS" /etc/login.defs | awk '{print $2}')
detail=$(grep PASS_MAX_DAYS /etc/login.defs)

# detail 변수의 값을 한 셀에 삽입하기 위해 큰따옴표로 묶고 줄바꿈 문자를 \n으로 변환
detail=$(echo "$detail" | sed ':a;N;$!ba;s/\n/\\n/g')

# 패스워드 최대 사용 기간이 90일 이내로 설정되어 있는 경우 양호
if [[ $password_max_age -le 90 ]]; then
    result="양호"
    # 결과를 csv 파일에 저장
    echo -e "계정관리,U-04,패스워드 최대 사용 기간 설정,중,$result,\"cat /etc/login.defs | grep PASS_MAX_DAYS의 결과입니다 : \n$detail\", 패스워드의 최대 사용기간이 90일 이내로 설정되어 있습니다." >> linux_report_$USER.csv
else
    result="취약"
    # 결과를 csv 파일에 저장
    echo -e "계정관리,U-04,패스워드 최대 사용 기간 설정,중,$result,\"cat /etc/login.defs | grep PASS_MAX_DAYS의 결과입니다 : \n$detail\",패스워드의 최대 사용기간이 90일 이내로 설정되어 있지 않습니다. 클라우드 취약점 점검 가이드를 참고하시어 \"/etc/login.defs\" 파일에 \"PASS_MAX_DAYS\"부분을 90일 이내로 설정하여 주시기 바랍니다." >> linux_report_$USER.csv
fi

#ok2
