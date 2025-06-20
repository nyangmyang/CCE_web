#!/bin/bash

# 진단 명령어 변수 정의 및 실행 결과 저장
passwd=$(grep "^ftp:" "/etc/passwd")
proftpd=$(cat /etc/proftpd/proftpd.con | grep -i "UserAlias" )
vsftpd=$(cat /etc/vsftpd/vsftpd.conf | grep -i "anonymous_enable=yes")

detail_vul='Anonymous FTP 접속을 차단하고 있지 않습니다. 클라우드 취약점 점검 가이드를 참고하시어 /etc/passwd 파일에서 ftp 또는 anonymous 계정을 삭제하거나 /etc/vsftpd/vsftpd.conf 또는 /etc/vsftpd.conf 파일에서 anonymous_enable=NO로 설정하여 주시기 바랍니다.'
detail_good='Anonymous FTP 접속을 차단하고 있습니다.'

# /etc/passwd 파일 확인
if [ -f "/etc/passwd" ]; then
    if grep -q "^ftp:" "/etc/passwd"; then
        result1='취약'
    else
        result1='양호'
    fi
fi

# /etc/proftpd/proftpd.conf 파일 확인
if [ -f "/etc/proftpd/proftpd.conf" ]; then
    if grep -v "^#" /etc/proftpd/proftpd.conf | grep -q "UserAlias"; then
        result2='취약'
    else
        result2='양호'
    fi
fi

# /etc/vsftpd/vsftpd.conf 파일 확인     
if [ -f "/etc/vsftpd/vsftpd.conf" ]; then
    if grep -iq "anonymous_enable=yes" "/etc/vsftpd/vsftpd.conf"; then
        result3='취약'
    else
        result3='양호'
    fi
fi

# 결과를 CSV 파일에 저장
if [ "$result1" = '양호' ] && [ "$result2" = '양호' ] && [ "$result3" = '양호' ]; then
    printf "서비스 관리,U-21,Anonymous FTP 비활성화,상,양호,\"/etc/passwd | grep ftp의 결과입니다 : $passwd\n*****\ngrep UserAlias /etc/proftpd/proftpd.conf && ! grep ^# /etc/proftpd/proftpd.conf | grep UserAlias의 결과입니다 : $proftpd\n*****\ngrep -iq anonymous_enable=yes /etc/vsftpd/vsftpd.conf의 결과입니다 : $vsftpd\",\"$detail_good\"\n" >> linux_report_$USER.csv
else
    printf "서비스 관리,U-21,Anonymous FTP 비활성화,상,취약,\"/etc/passwd | grep ftp의 결과입니다 : $passwd\n*****\ngrep UserAlias /etc/proftpd/proftpd.conf && ! grep ^# /etc/proftpd/proftpd.conf | grep UserAlias의 결과입니다 : $proftpd\n*****\ngrep -iq anonymous_enable=yes /etc/vsftpd/vsftpd.conf의 결과입니다 : $vsftpd\",\"$detail_vul\"\n" >> linux_report_$USER.csv
fi

# 세 개의 파일이 전부 없는 경우 N/A 처리
if [ ! -f "/etc/passwd" ] && [ ! -f "/etc/proftpd/proftpd.conf" ] && [ ! -f "/etc/vsftpd/vsftpd.conf" ]; then
    printf "서비스 관리,U-21,Anonymous FTP 비활성화,상,N/A,\"/etc/passwd | grep ftp의 결과입니다 : $passwd\n*****\ngrep UserAlias /etc/proftpd/proftpd.conf && ! grep ^# /etc/proftpd/proftpd.conf | grep UserAlias의 결과입니다 : $proftpd\n*****\ngrep -iq anonymous_enable=yes /etc/vsftpd/vsftpd.conf의 결과입니다 : $vsftpd\",\"Anonymous FTP를 사용하고 있지 않습니다.\"\n" >> linux_report_$USER.csv
fi

