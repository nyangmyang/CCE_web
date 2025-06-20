#!/bin/bash

# 서비스 사용 여부 확인
check_service_usage() {
    services=("rlogin" "shell" "exec")
    for service in "${services[@]}"; do
        if chkconfig --list "$service" 2>/dev/null | egrep '(on|활성)'; then
            echo "$service 서비스가 활성화되어 있습니다."
            return 1
        fi
    done
    return 0
}

# 파일 소유자 및 권한 확인
check_file_permissions() {
    file=$1
    if [ -e "$file" ]; then
        owner=$(stat -c %U "$file")
        permissions=$(stat -c %a "$file")

        if [ "$owner" != "root" ] && [ "$owner" != "$USER" ]; then
            echo "$file 파일 소유자가 root 또는 해당 계정이 아닙니다."
            return 1
        fi

        if [ "$permissions" -gt 600 ]; then
            echo "$file 파일 권한이 600 이하가 아닙니다."
            return 1
        fi

        if grep -q '+' "$file"; then
            echo "$file 파일에 '+' 설정이 포함되어 있습니다."
            return 1
        fi
    else
        echo "$file 파일이 존재하지 않습니다."
    fi
    return 0
}

# 메인 검사 함수
main() {
    # 서비스 사용 여부 확인
    check_service_usage
    service_usage_status=$?

    # 파일 소유자 및 권한 확인
    files_to_check=("/etc/hosts.equiv" "$HOME/.rhosts")
    file_status=0

    for file in "${files_to_check[@]}"; do
        check_file_permissions "$file"
        if [ $? -ne 0 ]; then
            file_status=1
        fi
    done

    # 결과 종합
    if [ $service_usage_status -eq 0 ] && [ $file_status -eq 0 ]; then
        result="양호"
        detail="모든 서비스가 비활성화되어 있고 파일 소유자 및 권한이 적절하게 설정되어 있습니다."
    else
        result="취약"
        detail="rlogin, shell, exec 서비스가 활성화되어 있거나 파일 소유자 및 권한이 적절하지 않습니다. 클라우드 취약점 점검 가이드를 참고하시어 \"/etc/hosts.equiv\" \"$HOME/.rhosts\" 파일의 root 또는, 해당 계정으로 변경하시고 권한을 600(-rw-------)로 설정하여 주시기 바랍니다."
    fi

    # 결과를 CSV 파일에 저장
# 결과 종합
if [ $service_usage_status -eq 0 ] && [ $file_status -eq 0 ]; then
    result="양호"
    detail="모든 서비스가 비활성화되어 있고 파일 소유자 및 권한이 적절하게 설정되어 있습니다."
else
    result="취약"
    detail="rlogin, shell, exec 서비스가 활성화되어 있거나 파일 소유자 및 권한이 적절하지 않습니다. 클라우드 취약점 점검 가이드를 참고하시어 \"/etc/hosts.equiv\" \"$HOME/.rhosts\" 파일의 root 또는, 해당 계정으로 변경하시고 권한을 600(-rw-------)로 설정하여 주시기 바랍니다."
fi

# 결과를 CSV 파일에 저장
if [ "$result" == "양호" ]; then
    echo -e "파일 및 디렉토리 관리,U-17,rlogin//shell//exec 서비스 비활성화,상,$result,\"chkconfig --list $service 2>/dev/null | egrep '(on|활성)' 결과입니다 : 그런 파일이나 디렉터리가 없습니다.${IFS}/etc/hosts.equiv $HOME/.rhosts 결과입니다 : 그런 파일이나 디렉터리가 없습니다.\",$detail" >> linux_report_$USER.csv
else
    echo -e "파일 및 디렉토리 관리,U-17,rlogin//shell//exec 서비스 비활성화,상,$result,\"chkconfig --list $service 2>/dev/null | egrep '(on|활성)' 결과입니다 : $service 서비스가 활성화되어 있습니다.${IFS}/etc/hosts.equiv $HOME/.rhosts 결과입니다 : 파일 소유자 및 권한을 확인하세요.\",$detail" >> linux_report_$USER.csv
fi
}

main
