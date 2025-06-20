#!/bin/bash

# result 변수에 값을 할당하는 부분 수정
if [ -f /etc/xinetd.d/finger ]; then
    result=$(cat /etc/xinetd.d/finger | grep disable | awk '{print $3}')

    if [ "$result" = "yes" ]; then
        detail="finger 서비스가 비활성화 되어 있는 상태입니다."
        echo "서비스 관리,U-20,Finger 서비스 비활성화,상,양호,\"$detail\"" >> linux_report_$USER.csv
    else
        detail="finger 서비스가 활성화 되어 있는 상태입니다. 클라우드 취약점 점검 가이드를 참고하시어 /etc/xinetd.d/finger 파일에서 finger 관련 설정을 비활성화하여 주시기 바랍니다."
        echo "서비스 관리,U-20,Finger 서비스 비활성화,상,취약,\"$detail\"" >> linux_report_$USER.csv
    fi
    exit 0
fi

if [ -f /etc/inetd.conf ]; then
    if grep -qE "finger" /etc/inetd.conf; then
        if grep -qE '^#.*finger|^finger' /etc/inetd.conf; then
            detail="finger 서비스가 활성화 되어 있는 상태입니다. 클라우드 취약점 점검 가이드를 참고하시어 /etc/inetd.conf 파일에서 finger 관련 설정을 비활성화하여 주시기 바랍니다."
            echo "서비스 관리,U-20,Finger 서비스 비활성화,상,취약,\"$detail\"" >> linux_report_$USER.csv
        else
            detail="finger 서비스가 비활성화 되어 있는 상태입니다."
            echo "서비스 관리,U-20,Finger 서비스 비활성화,상,양호,\"$detail\"" >> linux_report_$USER.csv
        fi
    fi
    exit 0
fi

# 서비스 파일이 존재하지 않는 경우
if [ ! -f "/etc/xinetd.d/finger" ] && [ ! -f "/etc/inetd.conf" ]; then
    result="N/A"
    detail="/etc /(x)inetd.d/finger 파일이 존재하지 않는 상태입니다."
    echo "서비스 관리,U-20,Finger 서비스 비활성화,상,N/A,\"cat /etc/xinetd.d/finger | grep disable | awk '{print \$3}'의 결과입니다 : 그런 파일이나 디렉터리가 없습니다.\",\"$detail\"" >> linux_report_$USER.csv
fi
