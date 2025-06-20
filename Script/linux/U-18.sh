#!/bin/bash

# 진단 명령어 변수 정의
deny=$(cat /etc/hosts.deny | tr '\n' ' ')
allow=$(cat /etc/hosts.allow | tr '\n' ' ')
# iptables=$(iptables -nL | tr '\n' ' ')
details='클라우드 취약점 점검 가이드를 참고하시어 접속을 허용할 특정 호스트에 대한 IP 주소 및 포트 제한을 설정하여 주시기 바랍니다.'

# 결과를 csv 파일에 저장, 절대 경로 사용
echo -e "파일 및 디렉토리 관리,U-18,접속 IP 및 포트 제한,상,N/A,\"cat /etc/hosts.deny의 결과입니다 : \n$deny\n\ncat /etc/hosts.allow의 결과입니다 : \n$allow\",$details" >> linux_report_$USER.csv
