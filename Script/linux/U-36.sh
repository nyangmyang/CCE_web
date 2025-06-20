#!/bin/bash

#:진단기준 
#양호 : 로그 기록의 검토, 분석, 리포트 작성 및 보고 등이 정기적으로 이루어지고 있는 경우
#취약 : 로그 기록의 검토, 분석, 리포트 작성 및 보고 등이 정기적으로 이루어지지 않는 경우

#:진단방법
#로그 정책 수립 여부 및 정책에 따른 로그 검토 여부 확인

#:조치방법
#-다음과 같이 로그 파일의 백업에 대한 검토를 해야 함
#1) su 시도에 관한 로그
#2) 반복적인 로그인 실패에 관한 로그
#3) 로그인 거부 메세지에 관한 로그
#4) 기본적 log 파일의 위치는 /var/dam, /var/log


#echo -e "패치 및 로그관리,U-36,로그의 정기적 검토 및 보고,상,N/A,기본적 log 파일의 위치는 /var/adm또는 /var/log입니다.,커널과 시스템에 관련된 로그 메시지들은 syslogd와 klogd 두개의 데몬에 의해 /var/log/messages에 기록하게 됩니다. /n/n이 파일을 분석함으로써 시스템을 항상 점검 관리해야 합니다." >> linux_report.csv

echo -e "패치 및 로그관리,U-36,로그의 정기적 검토 및 보고,상,인터뷰,담당자 확인이 필요한 항목입니다.,클라우드 취약점 점검 가이드를 참고하시어 로그 기록의 검토 분석 리포트 작성 및 보고 등이 정기적으로 이루어지고 있는지 점검하여 주시기 바랍니다." >> linux_report_$USER.csv
