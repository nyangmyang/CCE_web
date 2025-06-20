#!/bin/bash

#진단기준:
#양호 - 패치 적용 정책을 수립하여 주기적으로 패치를 관리하고 있는 경우
#취약 - 패치 적용 정책을 수립하여 주기적으로 패치를 관리하고 있지 않는 경우

#진단방법:
#패치 적용 정책 수립 여부 및 정책에 따른 패치 적용 여부 확인 
#https://github.com/mainsw/CSAP-CCE/blob/main/linux/U-35.sh
#조치방법:
#LINUX는 서버에 설치된 패치 리스트의 관리가 불가능하므로 rpm 패키지별 버그가 Fix된 최신 버전 설치가 필요함
#LINUX는 오픈되고, 커스터마이징 된 OS이므로 LINUX를 구입한 벤더에 따라 rpm 패키지가 다를 수 있으며, 아래의 사이트는 RedHat LINUX에 대한 버그 Fix 관련 사이트임
#<Red Hat 일 경우>
#1) 다음의 사이트에서 해당 버전을 찾음 http://www.redhat.com/security/updates/
# http://www.redhat.com/security/updates/eol/ (Red Hat LINUX 9 이하 버전)
#2) 발표된 Update 중 현재 사용 중인 보안 관련 Update 찾아 해당 Update Download
#3) Update 설치 
# # rpm -Uvh <pakage-name>

echo -e "패치 및 로그관리,U-35,최신 보안패치 및 벤더 권고사항 적용,상,인터뷰,담당자 확인이 필요한 항목입니다.,\"클라우드 취약점 점검 가이드를 참고하시어 발표된 중 현재 사용 중인 보안 관련 Update 찾아 해당 Update Download\n추가 점검 명령어 : rpm -Uvh <pakage-name>\"" >> linux_report_$USER.csv
