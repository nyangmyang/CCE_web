#!/bin/bash

# 점검할 파일과 예상되는 소유자 및 권한 설정
declare -A files=(
    ["/etc/crontab"]="root:root 640"
    ["/etc/cron.allow"]="root:root 640"
    ["/etc/cron.deny"]="root:root 640"
)

# 파일 점검 함수
check_file() {
    local file=$1
    local expected_owner_group=$2
    local expected_perm=$3

    # 파일이 존재하지 않으면 "그런 파일이나 디렉터리가 없습니다." 출력
    if [[ ! -e "$file" ]]; then
        echo "그런 파일이나 디렉터리가 없습니다."
        return 2
    fi

    # 실제 소유자 및 권한 가져오기
    local owner_group=$(stat -c "%U:%G" "$file")
    local perm=$(stat -c "%a" "$file")

    # 소유자 및 그룹, 권한 확인
    if [[ "$owner_group" != "$expected_owner_group" || "$perm" -gt "$expected_perm" ]]; then
        echo "취약"
        return 1
    else
        echo "양호"
        return 0
    fi
}

# Initialize detail and command_output variables
detail=""
command_output=""

# 각 파일에 대해 점검 수행
for file in "${!files[@]}"; do
    expected=${files[$file]}
    check_result=$(check_file "$file" ${expected% *} ${expected#* })
    file_command=$(ls -l "$file" 2>/dev/null)
    file_comment="ls -l $file의 결과입니다 : "

    if [[ $check_result == "취약" ]]; then
        detail="$detail$file 파일의 소유자 또는 권한이 예상 설정과 다릅니다. 클라우드 취약점 점검 가이드를 참고하시어 $file 파일의 소유자를 ${expected% *}로, 권한을 ${expected#* }로 설정하여 주시기 바랍니다.\n"
    elif [[ $check_result == "양호" ]]; then
        detail="$detail$file 파일의 소유자 및 권한이 예상대로 설정되어 있습니다.\n"
    else
        detail="$detail$file 그런 파일이나 디렉터리가 없습니다.\n"
    fi

    if [[ -n "$file_command" ]]; then
        command_output="$command_output$file_comment$file_command\n"
    else
        command_output="$command_output$file_comment그런 파일이나 디렉터리가 없습니다.\n"
    fi
done

# Determine final status
if [[ $detail == *"취약"* ]]; then
    overall_status="취약"
elif [[ $detail == *"양호"* ]]; then
    overall_status="양호"
else
    overall_status="N/A"
fi

# Append check result to report
echo -e "파일 및 디렉터리 관리,U-19,cron 파일 소유자 및 권한 설정,상,$overall_status,\"$command_output\",\"$detail\"" >> linux_report_$USER.csv
