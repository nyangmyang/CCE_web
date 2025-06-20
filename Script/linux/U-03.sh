#!/bin/bash

# /etc/pam.d/system-auth에서 preauth와 authfail의 deny 값 추출
preauth_system=$(grep -Po '^[^#]*pam_faillock.so.*preauth.*deny=\K\d+' /etc/pam.d/system-auth)
authfail_system=$(grep -Po '^[^#]*pam_faillock.so.*authfail.*deny=\K\d+' /etc/pam.d/system-auth)

# /etc/pam.d/password-auth에서 preauth와 authfail의 deny 값 추출
preauth_password=$(grep -Po '^[^#]*pam_faillock.so.*preauth.*deny=\K\d+' /etc/pam.d/password-auth)
authfail_password=$(grep -Po '^[^#]*pam_faillock.so.*authfail.*deny=\K\d+' /etc/pam.d/password-auth)

# 초기 상태 설정
final_result="양호"
message="계정 잠금 임계값이 5회 이하로 설정되어 있습니다."

# system-auth 파일 검사
if [[ -z $preauth_system ]] || ! [[ $preauth_system =~ ^[0-9]+$ ]] || (( preauth_system > 5 )) ||
   [[ -z $authfail_system ]] || ! [[ $authfail_system =~ ^[0-9]+$ ]] || (( authfail_system > 5 )); then
  final_result="취약"
  message="계정 잠금 임계값이 설정되어 있지 않거나 5 이하의 값으로 설정되어 있지 않은 상태입니다. 클라우드 취약점 점검 가이드를 참고하시어 \"/etc/pam.d/system-auth\" 파일 내 \"auth\" 설정 값에 \"deny\" 부분을 5 이하의 값으로 설정하여 주시기 바랍니다. (preauth: $preauth_system, authfail: $authfail_system)"
fi

# password-auth 파일 검사
if [[ -z $preauth_password ]] || ! [[ $preauth_password =~ ^[0-9]+$ ]] || (( preauth_password > 5 )) ||
   [[ -z $authfail_password ]] || ! [[ $authfail_password =~ ^[0-9]+$ ]] || (( authfail_password > 5 )); then
  final_result="취약"
  message="계정 잠금 임계값이 설정되어 있지 않거나 5 이하의 값으로 설정되어 있지 않은 상태입니다. 클라우드 취약점 점검 가이드를 참고하시어 \"/etc/pam.d/password-auth\" 파일 내 \"auth\" 설정 값에 \"deny\" 부분을 5 이하의 값으로 설정하여 주시기 바랍니다. (preauth: $preauth_password, authfail: $authfail_password)"
fi

# 결과 출력 (한 줄로 결합)
echo -e "계정관리,U-03,계정 잠금 임계값 설정,상,$final_result,\"/etc/pam.d/system-auth의 preauth와 authfail의 deny 값 : preauth $preauth_system, authfail $authfail_system,\n/etc/pam.d/password-auth의 preauth와 authfail의 deny 값 : preauth $preauth_password, authfail $authfail_password\",\"$message\"" >> linux_report_$USER.csv
