#!/bin/bash

final_result="양호" # 최종 결과 기본값을 양호로 설정
detail=""

check_service() {
  local service=$1
  local result="양호"
  for i in $(ls /etc/xinetd.d/$service* 2>/dev/null)
  do
    if [ "$(grep 'disable' $i | awk '{print $3}')" != "yes" ]; then
      result="취약"
      break
    fi
  done
  echo $result
}

# 각 서비스를 검사하고 하나라도 취약하면 final_result를 취약으로 설정
for service in echo discard daytime chargen; do
  if ls /etc/xinetd.d/$service* >/dev/null 2>&1; then
    result=$(check_service $service)
    if [ "$result" = "취약" ]; then
      final_result="취약"
      break
    fi
  fi
done

# detail 변수 설정
if [ "$final_result" = "양호" ]; then
  detail="Dos (echo//discard//daytime//chargen) 공격에 취약한 서비스가 비활성화된 상태입니다."
else
  detail="Dos (echo//discard//daytime//chargen) 공격에 취약한 서비스가 활성화된 상태입니다. 클라우드 취약점 점검 가이드를 참고하시어 /etc/xinetd.d/ 디렉터리 내 echo, discard, daytime, chargen 파일 내 관련 설정을 주석처리하거나 disable=yes로 설정하여 주시기 바랍니다."
fi

# 각 파일의 disable 상태를 확인 후 결과를 변수에 저장
echo_result=$(if [ -f /etc/xinetd.d/echo ]; then cat /etc/xinetd.d/echo | grep disable; else echo "서비스가 비활성화 되어 있습니다."; fi)
discard_result=$(if [ -f /etc/xinetd.d/discard ]; then cat /etc/xinetd.d/discard | grep disable; else echo "서비스가 비활성화 되어 있습니다."; fi)
daytime_result=$(if [ -f /etc/xinetd.d/daytime ]; then cat /etc/xinetd.d/daytime | grep disable; else echo "서비스가 비활성화 되어 있습니다."; fi)

# 결과 출력
echo -e "서비스 관리,U-23,DOS 공격에 취약한 서비스 비활성화,상,$final_result,\"cat /etc/xinetd.d/echo | grep disable의 결과입니다 : $echo_result\ncat /etc/xinetd.d/discard | grep disable의 결과입니다 : $discard_result\ncat /etc/xinetd.d/daytime | grep disable의 결과입니다 : $daytime_result\",$detail" >> linux_report_$USER.csv
