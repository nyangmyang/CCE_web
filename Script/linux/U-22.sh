#!/bin/bash

ls /etc/xinetd.conf* >/dev/null 2>&1
if [ $? != 0 ]; then 
    echo ''
else
    for i in $(ls /etc/xinetd.conf*); do
        if grep -qE "rsh|rlogin|rexec" "$i"; then
            if [ "$(cat "$i" | grep disable | awk '{print $3}')" = "yes" ]; then
                detail="r (rlogin, rsh, rexec) 계열 서비스가 비활성화 되어 있는 상태입니다."
                echo "서비스 관리,U-22,r 계열 서비스 비활성화,상,양호,\"$detail\"" >> linux_report.csv
            else
                detail="r (rlogin, rsh, rexec) 계열 서비스가 활성화 되어 있는 상태입니다."
                echo "서비스 관리,U-22,r 계열 서비스 비활성화,상,취약,\"$detail\"" >> linux_report.csv
            fi
        else
            detail="r (rlogin, rsh, rexec) 계열 서비스가 비활성화 되어 있는 상태입니다."
            echo "서비스 관리,U-22,r 계열 서비스 비활성화,상,양호,\"$detail\"" >> linux_report.csv
        fi
    done
fi

if [ ! -d "/etc/xinetd.d" ] && [ ! -f "/etc/inetd.conf" ]; then
    detail="r (rlogin, rsh, rexec) 계열 서비스가 비활성화 되어 있는 상태입니다."
    echo "서비스 관리,U-22,r 계열 서비스 비활성화,상,N/A,\"$detail\"" >> linux_report_$USER.csv
    exit
fi

get_disable_status() {
    local service_file=$1
    if [ -f "$service_file" ]; then
        local status=$(awk -F= '/disable/ {print $2}' "$service_file" | tr -d ' ')
        if [ "$status" = "yes" ]; then
            echo 1
        else
            echo 0
        fi
    else
        echo 1 # 파일이 없으면 서비스가 비활성화되었다고 가정하고 1을 반환
    fi
}

# 각 파일의 disable 상태를 확인 후 결과를 변수에 저장
rlogin_result=$(if [ -f /etc/xinetd.d/rlogin ]; then cat /etc/xinetd.d/rlogin | grep disable; else echo "서비스가 비활성화 되어 있습니다."; fi)
rsh_result=$(if [ -f /etc/xinetd.d/rsh ]; then cat /etc/xinetd.d/rsh | grep disable; else echo "서비스가 비활성화 되어 있습니다."; fi)
rexec_result=$(if [ -f /etc/xinetd.d/rexec ]; then cat /etc/xinetd.d/rexec | grep disable; else echo "서비스가 비활성화 되어 있습니다."; fi)

rlogin_flag=$(get_disable_status /etc/xinetd.d/rlogin)
rsh_flag=$(get_disable_status /etc/xinetd.d/rsh)
rexec_flag=$(get_disable_status /etc/xinetd.d/rexec)

if [ $rlogin_flag -eq 1 ] && [ $rsh_flag -eq 1 ] && [ $rexec_flag -eq 1 ]; then
    detail="r (rlogin//rsh//rexec) 계열 서비스가 비활성화 되어 있는 상태입니다."
    echo -e "서비스 관리,U-22,r 계열 서비스 비활성화,상,양호,\"rlogin disable 상태:$rlogin_result\nrsh disable 상태:$rsh_result\nrexec disable 상태:$rexec_result\",$detail" >> linux_report_$USER.csv
else
    detail="r (rlogin//rsh//rexec) 계열 서비스가 활성화 되어 있는 상태입니다. 클라우드 취약점 점검 가이드를 참고하시어 /etc/xinetd.d/ 디렉터리 내 rlogin, rsh, rexec 파일 내 관련 설정을 주석처리하거나 disable=yes로 설정하여 주시기 바랍니다."
    echo -e "서비스 관리,U-22,r 계열 서비스 비활성화,상,취약,\"rlogin disable 상태:$rlogin_result\nrsh disable 상태:$rsh_result\nrexec disable 상태:$rexec_result\",$detail" >> linux_report_$USER.csv
fi

unset rlogin_flag rsh_flag rexec_flag
