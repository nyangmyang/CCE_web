#!/bin/bash

CODE="U-08"
VULN=false

detail=$(ls -l /etc/passwd)

# /etc/passwd가 없는 경우 비정상 종료
if [[ ! -e "/etc/passwd" ]]; then
    echo "[$CODE] N/A: /etc/passwd does not exist."
		if [ -e "linux_report_$USER.csv" ]; then
			echo "파일 및 디렉토리 관리,$CODE,/etc/passwd 파일 소유자 및 권한 설정,상,N/A,/etc/passwd 파일이 존재하지 않습니다.,수동 점검이 필요한 항목입니다." >> linux_report_$USER.csv
			echo "[$CODE] Report generated."
		else
			echo "구분,진단 코드,진단 항목,취약도,점검 결과" > linux_report_$USER.csv
			echo "파일 및 디렉토리 관리,$CODE,/etc/passwd 파일 소유자 및 권한 설정,상,N/A,/etc/passwd 파일이 존재하지 않습니다.,수동 점검이 필요한 항목입니다." >> linux_report_$USER.csv
			echo "[$CODE] Report generated."
		fi
    exit 1
fi

# /etc/passwd 파일의 소유자가 root인지 확인
if [ "$(stat -c '%U' /etc/passwd)" != "root" ]; then
	echo "[$CODE] VULN: The owner of /etc/passwd is not root."
	VULN=true
fi

# /etc/passwd 파일의 권한이 644 이하인지 확인
if [ "$(stat -c '%a' /etc/passwd)" -gt 644 ]; then
	echo "[$CODE] VULN: The permissions of /etc/passwd are not 644 or less."
	VULN=true
fi

# 취약점이 발견되지 않았을 경우 메시지 출력
if [ "$VULN" = false ]; then
    echo "[$CODE] OK: No vulnerability found"
fi

# VULN 값에 따라 취약 / 양호 레포트 작성.
if [ "$VULN" = true ]; then
    REPORT="파일 및 디렉토리 관리,$CODE,/etc/passwd 파일 소유자 및 권한 설정,상,취약,\"ls -l /etc/passwd의 결과입니다 : \n$detail\",/etc/passwd 파일의 소유자가 root가 아니거나 권한이 644초과인 경우입니다. 클라우드 취약점 점검 가이드를 참고하시어 \"/etc/passwd\"파일의 소유자를 root로 변경하시고 권한을 644(-rw-r--r--)로 설정하여 주시기 바랍니다."
else
    REPORT="파일 및 디렉토리 관리,$CODE,/etc/passwd 파일 소유자 및 권한 설정,상,양호,\"ls -l /etc/passwd의 결과입니다 : \n$detail\",/etc/passwd 파일의 소유자가 root이고 권한이 644이하인 상태입니다."
fi

# 파일이 존재하면 이어서 작성, 존재하지 않으면 보고서 헤더 작성 후 레포트 작성.
if [ -e "linux_report_$USER.csv" ]; then
    echo -e "$REPORT" >> linux_report_$USER.csv
    echo "[$CODE] Report generated."
else
    echo "구분,진단 코드,진단 항목,취약도,점검 결과" > linux_report_$USER.csv
    echo -e "$REPORT" >> linux_report_$USER.csv
    echo "[$CODE] Report generated."
fi

exit 0