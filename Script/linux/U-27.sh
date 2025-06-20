export LANG=ko_KR.UTF-8
#!/bin/bash

# /etc/xinetd.d/rstatd 존재하지 않을 시 N/A 처리
if [ ! -e "/etc/xinetd.d/rstatd" ] || [ ! -e "/etc/inetd.conf" ] ; then
  detail="/etc/xinetd.d/rstatd 파일이 존재하지 않는 상태입니다."
  command=$(cat /etc/xinetd.d/rstatd)
  comment="cat /etc/xinetd.d/rstatd의 결과값입니다 : "
  echo -e "서비스 관리,U-27,RPC 서비스 확인,상,양호,\"$comment \n$command\",$detail">> linux_report_$USER.csv
  exit 1
fi

if [ -f /etc/xinetd.d/rstatd ] ; then
cat /etc/xinetd.d/rstatd >/dev/null 2>&1
if [ $? -ne 0 ] ; then
	# 불필요한 RPC 서비스가 비활성화 되어 있는 경우
   detail="불필요한 RPC 서비스가 비활성화되어 있는 상태입니다."
   command=$(cat /etc/xinetd.d/rstatd >/dev/null 2>&1)
   comment="cat /etc/xinetd.d/rstatd >dev/null 2>&1의 결과값입니다 : "
	echo -e "서비스 관리,U-27,RPC 서비스 확인,상,양호,\"$comment \n$command\",$detail">> linux_report_$USER.csv
else
	# 불필요한 RPC 서비스가 활성화 되어 있는 경우
   detail="불필요한 RPC 서비스가 활성화되어 있는 상태입니다. 클라우드 취약점 점검 가이드를 참고하시어 /etc/xinetd.d/ 디렉터리 내의 불필요한 RPC 서비스 파일 내 관련 설정을 주석처리하거나 disable=yes로 설정하여 주시기 바랍니다."
   comment=$(cat /etc/xinetd.d/rstatd >/dev/null 2>&1)
   comment="cat /etc/xinetd.d/rstatd >dev/null 2>&1의 결과값입니다 : "
	echo -e "서비스 관리,U-27,RPC 서비스 확인,상,취약,\"$comment \n$command\",$detail">> linux_report_$USER.csv
fi
fi

if [ -f /etc/inetd.conf ] ; then
cat /etc/inetd.conf | grep rpc.cmsd >/dev/null 2>&1
if [ $? -ne 0 ] ; then
	# 불필요한 RPC 서비스가 비활성화 되어 있는 경우
   detail="불필요한 RPC 서비스가 비활성화되어 있는 상태입니다."
   command=$(cat /etc/inetd.conf | grep rpc.cmsd >/dev/null 2>&1)
   comment="cat /etc/inetd.conf | grep rpc.cmsd >dev/null 2>&1의 결과값입니다 : "
	echo -e "서비스 관리,U-27,RPC 서비스 확인,상,양호,\"$comment \n$command\",$detail">> linux_report_$USER.csv
else
	# 불필요한 RPC 서비스가 활성화 되어 있는 경우
   detail="불필요한 RPC 서비스가 활성화되어 있는 상태입니다. 클라우드 취약점 점검 가이드를 참고하시어 /etc/inetd.conf 파일 내 불필요한 RPC 서비스 관련 설정을 주석처리하거나 disable=yes로 설정하여 주시기 바랍니다."
   comment=$(cat /etc/inetd.conf | grep rpc.cmsd >/dev/null 2>&1)
   comment="cat /etc/inetd.conf | grep rpc.cmsd >dev/null 2>&1의 결과값입니다 : "
	echo -e"서비스 관리,U-27,RPC 서비스 확인,상,취약,\"$comment \n$command\",$detail">> linux_report_$USER.csv
fi
fi
