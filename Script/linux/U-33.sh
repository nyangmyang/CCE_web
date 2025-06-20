#!/bin/bash

# DNS 서비스 확인
if [ $(ps -ef | grep named | grep -v grep | wc -l) -eq 0 ]; then
    # DNS 서비스 미사용
    result="양호"
    detail=$(ps -ef | grep named | grep -v grep | wc -l)
  
    echo "서비스 관리,U-33,DNS 보안 버전 패치,상,$result,ps -ef | grep named | grep -v grep | wc -l의 결과입니다 : $detail,DNS 서비스를 사용하고 있지 않습니다." >> linux_report_$USER.csv
else
    # DNS 서버 사용
    detail=$(ps -ef | grep named | grep -v grep | wc -l)

    # BIND 버전 확인
    bind_version=$(named -v | grep BIND | awk '{print $2}')

    # 최신 버전 확인 (참고: Fedora 시스템에서는 DNF를 사용)
    latest_version=$(dnf info bind | grep '^Version' | awk '{print $3}' | sort -V | tail -n1)

    if [ "$bind_version" == "$latest_version" ]; then
        # 최신 버전일 때
        result="양호"
        echo "서비스 관리,U-33,DNS 보안 버전 패치,상,$result,현재 사용 중인 BIND 버전: $bind_version, 최신 BIND 버전: $latest_version, DNS 서비스를 사용하고 있으며 주기적으로 패치를 관리하고 있습니다." >> linux_report_$USER.csv
    else
        # 최신 버전이 아닐 때
        result="취약"
        echo "서비스 관리,U-33,DNS 보안 버전 패치,상,$result,현재 사용 중인 BIND 버전: $bind_version, 최신 BIND 버전: $latest_version, DNS 서비스를 사용하고 있으며 주기적으로 패치를 관리하고 있지 않습니다. 클라우드 취약점 점검 가이드를 참고하시어 BIND 버전 확인 후 최신 버전으로 업데이트하여 주시기 바랍니다." >> linux_report_$USER.csv
    fi
fi