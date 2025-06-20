#!/bin/bash

# /etc/pam.d/system-auth 파일이 있는지 확인
if [[ ! -f "/etc/pam.d/system-auth" ]]; then
  echo "ERROR: /etc/pam.d/system-auth file not found!"
  exit 1
fi

# enforce_for_root 설정 확인
if grep -q "enforce_for_root" /etc/pam.d/system-auth; then
  enforce_root="설정되어 있습니다"
else
  enforce_root="설정되어 있지 않습니다"
fi

# lcredit, dcredit, ucredit, ocredit 중 몇 개가 포함되어 있는지 확인
credit_count=0
if grep -q "lcredit" /etc/pam.d/system-auth; then
  ((credit_count++))
fi
if grep -q "dcredit" /etc/pam.d/system-auth; then
  ((credit_count++))
fi
if grep -q "ucredit" /etc/pam.d/system-auth; then
  ((credit_count++))
fi
if grep -q "ocredit" /etc/pam.d/system-auth; then
  ((credit_count++))
fi

# minlen 값을 읽어옴
minlen=$(grep -E "minlen=[0-9]+" /etc/security/pwquality.conf | sed -E 's/.*minlen=([0-9]+).*/\1/')

# pwquality.conf 파일에서 복잡도 설정 값 확인
pwquality_config=$(grep -E "lcredit|dcredit|ucredit|ocredit|minlen" /etc/security/pwquality.conf)

# credit 옵션이 2개 이상이고 minlen이 10 이상인 경우 양호로 판단
if [[ $credit_count -eq 2 && $minlen -ge 10 ]]; then
  result="양호"
  detail="옵션이 2개이고 minlen이 10 이상입니다."
# credit 옵션이 3개 이상이고 minlen이 8 이상인 경우 양호로 판단
elif [[ $credit_count -eq 3 && $minlen -ge 8 ]]; then
  result="양호"
  detail="옵션이 3개이고 minlen이 8 이상입니다."
elif [[ $credit_count -eq 4 && $minlen -ge 8 ]]; then
  result="양호"
  detail="옵션이 4개이고 minlen이 8 이상입니다."
else
  result="취약"
  detail="패스워드 복잡성 또는 패스워드 최소길이를 만족하지 않습니다. 클라우드 취약점 점검 가이드를 참고하시어 패스워드 복잡도 설정 값(최소 자리수 영문 대/소문자 특수문자 숫자)을 사내 내부 규정에 맞게 복잡도를 설정하여 주시기 바랍니다."
fi

# 결과를 csv 파일에 저장
echo -e "계정관리,U-02,패스워드 복잡성 설정,상,$result,\"cat /etc/pam.d/system-auth | grep minlen | awk '{print \\\$7}'의 결과값입니다 : minlen=$minlen \ncat /etc/pam.d/system-auth | grep minlen | awk '{print \\\$8, \\\$9, \\\$10, \\\$11}'의 결과값입니다 : credit=$credit \n패스워드 복잡도 설정 값: $pwquality_config \nenforce_for_root 설정: $enforce_root\",$detail" >> linux_report_$USER.csv
