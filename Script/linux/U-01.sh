#!/bin/bash
export LANG=ko_KR.UTF-8

# CSV 파일이 존재하지 않으면 헤더 추가
if [ ! -e "linux_report.csv" ]; then
    echo "구분,진단코드,진단항목,취약도,점검결과,시스템 실제 결과값,상세설명 및 조치방안" > linux_report_$USER.csv
fi

# /etc/securetty가 없는 경우 telnet이 비활성화된 것으로 간주
if [[ ! -e "/etc/securetty" ]]; then
    securetty_result="양호"
    command1="cat /etc/securetty"
    comment1="cat /etc/securetty의 결과값입니다 : "
    detail1="/etc/securetty 파일이 존재하지 않으며, telnet이 비활성화된 것으로 간주합니다. (CentOS 8, Ubuntu 20.04 이상에서 기본 상태)"
else
    # /etc/securetty 파일에 pts/0 ~ pts/x 관련 설정이 포함되어 있는지 확인
    if grep -q "pts/[0-9]" /etc/securetty; then
        securetty_result="취약"
        command1=$(grep "pts" /etc/securetty)
        comment1="cat /etc/securetty의 결과값입니다 : "
        detail1="/etc/securetty 파일에 pts/0 ~ pts/x 관련 설정이 포함되어 있습니다. 클라우드 취약점 점검 가이드를 참고하여 해당 설정을 제거하거나 주석 처리하시기 바랍니다."
    else
        securetty_result="양호"
        command1=$(grep "pts" /etc/securetty)
        comment1="cat /etc/securetty의 결과값입니다 : "
        detail1="/etc/securetty 파일에 pts/0 ~ pts/x 관련 설정이 포함되어 있지 않습니다."
    fi
fi

# SSH를 통해 루트 로그인이 허용되는지 확인 (대소문자 구분 없이 yes, YES, Yes 체크, 주석도 취약으로 간주)
if grep -q -i "^PermitRootLogin\s*no" /etc/ssh/sshd_config; then
    ssh_result="양호"
    command2=$(grep -i "^PermitRootLogin" /etc/ssh/sshd_config)
    comment2="cat /etc/ssh/sshd_config | grep PermitRootLogin의 결과값입니다 : "
    detail2="SSH를 통한 루트 로그인이 허용되지 않은 상태입니다."
elif grep -iq "^\s*#\s*PermitRootLogin\s*yes" /etc/ssh/sshd_config || grep -iq "^PermitRootLogin\s*yes" /etc/ssh/sshd_config; then
    ssh_result="취약"
    command2=$(grep -i "^PermitRootLogin" /etc/ssh/sshd_config)
    comment2="cat /etc/ssh/sshd_config | grep PermitRootLogin의 결과값입니다 : "
    detail2="SSH를 통한 루트 로그인이 허용된 상태입니다. 클라우드 취약점 점검 가이드를 참고하여 PermitRootLogin 설정을 no로 변경하시기 바랍니다."
else
    ssh_result="취약"
    command2="PermitRootLogin 설정이 없습니다."
    comment2="cat /etc/ssh/sshd_config의 결과값입니다 : "
    detail2="SSH 설정 파일에서 PermitRootLogin 설정이 누락되었습니다. 클라우드 취약점 점검 가이드를 참고하여 PermitRootLogin 설정을 no로 추가하십시오."
fi

# 최종 결과 결정
if [[ "$securetty_result" == "취약" || "$ssh_result" == "취약" ]]; then
    result="취약"
else
    result="양호"
fi

# 결과를 csv 파일에 저장
echo -e "계정관리,U-01,root 계정 원격 접속 제한,상,$result,\"$comment1 $command1\n$comment2 $command2\",$detail1*****$detail2" >> linux_report_$USER.csv
