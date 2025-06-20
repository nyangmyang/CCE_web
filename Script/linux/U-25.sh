#!/bin/bash

export LANG=ko_KR.UTF-8

if showmount -e localhost &>/dev/null; then
	#nfs 서비스가 실행 중인지 확인
	CHECK1=$(service nfs status | grep -o "is running")
	HOSTNAME=$(hostname)
	#호스트명된 디렉토리에서 'everyone' 문자열이 있는 줄 수
	CHECK2=$(showmount -e $HOSTNAME | grep everyone | wc -l)
	if [ -z "$CHECK1" ] || [ $CHECK2 -eq 0 ]; then
      detail="NFS 서비스를 사용하고 있으며 everyone 공유를 제한하고 있는 상태입니다."
      command=$(showmount -e $HOSTMANE | grep everyone | wc -l)
      comment="showmount -e \$HOSTNAME | grep everyone | wc -l의 결과값입니다 : "
		echo "서비스 관리,U-25,NFS 접근통제,상,양호,$comment $command, $detail" >> linux_report_$USER.csv
	else
      detail="NFS 서비스를 사용하고 있으며 everyone 공유를 제한하고 있지 않은 상태입니다. 클라우드 취약점 점검 가이드를 참고하시어 everyone 마운트를 제거하시고 /etc/exports 파일에서 접근 통제 설정을 해주시기 바랍니다."
      command=$(showmount -e $HOSTMANE | grep everyone | wc -l)
      comment="showmount -e \$HOSTNAME | grep everyone | wc -l의 결과값입니다 : "
		echo "서비스 관리,U-25,NFS 접근통제,상,취약, $comment $command, $detail" >> linux_report_$USER.csv
	fi
else
   detail="NFS 서비스를 사용하고 있지 않은 상태입니다."
   command=$(showmount -e localhost &>/dev/null)
   comment="showmount -e localhost &>dev/null의 결과값입니다 : "
	echo "서비스 관리,U-25,NFS 접근통제,상,N/A,$comment $command,$detail" >> linux_report_$USER.csv
	exit 1
fi
