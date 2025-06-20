import os
import yaml
import tempfile
import ansible_runner
from datetime import datetime
from typing import List, Dict
from collections import defaultdict

def run_ansible_playbook_on_hosts(host_list: List[Dict[str, str]]) -> bool:
    """
    Execute Ansible playbook on multiple hosts grouped by OS type.
    
    Args:
        host_list: List of dictionaries containing host information
                  Each dict should have: HOST_IDEN, HOST_ADDR, HOST_USER, HOST_PORT, HOST_SUPW, HOST_OS
    
    Returns:
        bool: True if all OS groups successful, False otherwise
    """
    
    # Group hosts by OS type
    os_groups = group_hosts_by_os(host_list)
    
    overall_success = True
    
    # Process each OS group separately
    for os_type, hosts in os_groups.items():
        print(f"\n{'='*50}")
        print(f"Processing {len(hosts)} {os_type} hosts...")
        print(f"{'='*50}")
        
        # Check if script exists for this OS type
        script_path = get_script_path(os_type)
        if not os.path.exists(script_path):
            print(f"Warning: Script {script_path} not found. Skipping {os_type} hosts.")
            overall_success = False
            continue
        
        # Create inventory for this OS group
        inventory = create_os_inventory(hosts, os_type)
        
        # Create playbook for this OS type
        playbook = create_os_playbook(os_type)
        
        # Create extravars
        extravars = create_extravars(hosts)
        
        # Execute playbook for this OS group
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                print(f"Executing {os_type} playbook using ansible_runner...")
                
                result = ansible_runner.run(
                    private_data_dir=temp_dir,
                    inventory=inventory,
                    playbook=playbook,
                    extravars=extravars,
                    quiet=False,
                    verbosity=1
                )
                
                if result.status == 'successful':
                    print(f"✓ {os_type} playbook executed successfully!")
                    
                    # Print host-specific results
                    for event in result.events:
                        if event.get('event') == 'runner_on_ok':
                            task_name = event.get('event_data', {}).get('task', 'Unknown task')
                            host = event.get('event_data', {}).get('host', 'Unknown host')
                            if 'Fetch JSON file' in task_name:
                                print(f"  ✓ JSON file retrieved from {host}")
                else:
                    print("No hosts are manageable by Ansible. Please check your configuration.")
                    print(f"✗ {os_type} playbook failed with status: {result.status}")
                    overall_success = False
                    
                    # Print error details
                    for event in result.events:
                        if event.get('event') in ['runner_on_failed', 'runner_on_unreachable']:
                            host = event.get('event_data', {}).get('host', 'Unknown host')
                            res = event.get('event_data', {}).get('res', {})
                            msg = res.get('msg', res.get('stderr', 'Unknown error'))
                            print(f"  ✗ Error on {host}: {msg}")
                            
            except Exception as e:
                print(f"✗ Error executing {os_type} playbook: {e}")
                overall_success = False
    
    return overall_success

def group_hosts_by_os(host_list: List[Dict[str, str]]) -> Dict[str, List[Dict[str, str]]]:
    """Group hosts by their OS type, extracting base OS from version strings."""
    os_groups = defaultdict(list)
    
    for host in host_list:
        os_full = host.get('HOST_OS', 'else')
        
        # Extract base OS type from full OS string (e.g., "Ubuntu 24.04" -> "ubuntu")
        os_base = extract_base_os_type(os_full)
        
        # Normalize OS names to standard categories
        if os_base in ['ubuntu', 'debian']:
            os_type = 'Ubuntu'
        elif os_base in ['centos', 'rhel', 'redhat', 'fedora', 'rocky', 'almalinux']:
            os_type = 'CentOS'
        elif os_base in ['windows', 'win']:
            os_type = 'Windows'
        else:
            os_type = 'else'
        
        # Update the host dict with normalized OS and keep original
        host_copy = host.copy()
        host_copy['HOST_OS_TYPE'] = os_type  # Normalized type for scripts
        host_copy['HOST_OS_FULL'] = os_full  # Original full OS string
        os_groups[os_type].append(host_copy)
    
    return dict(os_groups)

def extract_base_os_type(os_string: str) -> str:
    """
    Extract base OS type from full OS string.
    
    Examples:
        "Ubuntu 24.04" -> "ubuntu"
        "CentOS 8.5" -> "centos"
        "Windows Server 2019" -> "windows"
        "Red Hat Enterprise Linux 9.2" -> "redhat"
    """
    if not os_string:
        return 'else'
    
    # Convert to lowercase and split by spaces
    os_parts = os_string.lower().split()
    
    if not os_parts:
        return 'else'
    
    first_word = os_parts[0]
    
    # Handle special cases
    if first_word == 'red' and len(os_parts) > 1 and os_parts[1] == 'hat':
        return 'redhat'
    elif first_word == 'windows':
        return 'windows'
    elif first_word in ['ubuntu', 'debian', 'centos', 'fedora', 'rocky', 'almalinux']:
        return first_word
    elif 'rhel' in first_word or 'redhat' in first_word:
        return 'redhat'
    elif 'win' in first_word:
        return 'windows'
    else:
        return 'else'

def get_script_path(os_type: str) -> str:
    """Get the script path for the given OS type."""
    script_names = {
        'Ubuntu': 'script/Ubuntu/Ubuntu_cce.sh',
        'CentOS': 'script/CentOS/CentOS_cce.sh', 
        'Windows': 'script/Windows/Windows_cce.bat',
        'else': 'script/else/else_cce.sh'
    }
    
    return os.path.join(os.getcwd(), script_names.get(os_type, 'Script/else/else.sh'))

def create_os_inventory(host_list: List[Dict[str, str]], os_type: str) -> dict:
    """Create Ansible inventory dictionary for specific OS type."""
    group_name = f"{os_type.lower()}_hosts"
    
    inventory = {
        group_name: {
            'hosts': {}
        }
    }
    
    for i, host in enumerate(host_list):
        host_name = f"{os_type.lower()}_host_{i}"
        host_config = {
            'ansible_host': host['HOST_ADDR'],
            'ansible_user': host['HOST_USER'],
            'ansible_port': int(host['HOST_PORT']),
            'ansible_become_password': host['HOST_SUPW'],
            'ansible_ssh_common_args': '-o StrictHostKeyChecking=no',
            'host_os_type': host['HOST_OS_TYPE'],
            'host_os_full': host['HOST_OS_FULL'],
            'host_ip': host['HOST_ADDR'],
            'host_identifier': host['HOST_IDEN']
        }
        
        # Windows-specific configuration
        if os_type == 'Windows':
            host_config.update({
                'ansible_connection': 'winrm',
                'ansible_winrm_transport': 'basic',
                'ansible_winrm_server_cert_validation': 'ignore'
            })
        
        inventory[group_name]['hosts'][host_name] = host_config
    
    return inventory

def create_os_playbook(os_type: str) -> list:
    """Create the Ansible playbook for specific OS type."""
    group_name = f"{os_type.lower()}_hosts"
    script_name = get_script_filename(os_type)
    
    if os_type == 'Windows':
        return create_windows_playbook(group_name, script_name)
    elif os_type == 'else':
        return create_else_playbook(group_name)
    else:
        return create_unix_playbook(group_name, script_name)

def get_script_filename(os_type: str) -> str:
    """Get script filename for the OS type."""
    script_names = {
        'Ubuntu': 'Ubuntu_cce.sh',
        'CentOS': 'CentOS_cce.sh',
        'Windows': 'Windows_cce.bat',
        'else': 'else_cce.sh'
    }
    return script_names.get(os_type, 'else_cce.sh')

def create_unix_playbook(group_name: str, script_name: str) -> list:
    """Create playbook for Unix-like systems (Ubuntu, CentOS)."""
    # Extract OS type from group_name (e.g., "ubuntu_hosts" -> "Ubuntu")
    os_type = group_name.replace('_hosts', '')
    if os_type == 'ubuntu':
        os_type = 'Ubuntu'
    elif os_type == 'centos':
        os_type = 'CentOS'
    
    script_path = get_script_path(os_type)
    
    playbook = [{
        'name': f'Execute {script_name} on {group_name}',
        'hosts': group_name,
        'become': True,
        'gather_facts': True,
        'vars': {
            'script_name': script_name,
            'script_path': script_path,
            'local_dir': os.getcwd(),
            'tmp_dir': os.path.join(os.getcwd(), 'tmp')
        },
        'tasks': [
            {
                'name': 'Create tmp directory on control node',
                'local_action': {
                    'module': 'file',
                    'path': "{{ tmp_dir }}",
                    'state': 'directory'
                },
                'become': False,
                'run_once': True
            },
            {
                'name': f'Copy {script_name} to host',
                'copy': {
                    'src': "{{ script_path }}",
                    'dest': "/tmp/{{ script_name }}",
                    'mode': '0755'
                }
            },
            {
                'name': f'Execute {script_name}',
                'command': f'/tmp/{script_name}',
                'args': {
                    'chdir': '/tmp'
                },
                'register': 'script_result'
            },
            {
                'name': 'Find generated JSON files',
                'find': {
                    'paths': ['/tmp'],
                    'patterns': ['{{ host_os_type }}_*.json']
                },
                'register': 'json_files'
            },
            {
                'name': 'Fetch JSON files to control node tmp directory',
                'fetch': {
                    'src': "{{ item.path }}",
                    'dest': "{{ tmp_dir }}/",
                    'flat': True
                },
                'loop': "{{ json_files.files }}"
            },
            {
                'name': 'Rename JSON files to use HOST_IDEN',
                'local_action': {
                    'module': 'copy',
                    'src': "{{ tmp_dir }}/{{ item.path | basename }}",
                    'dest': "{{ tmp_dir }}/{{ host_identifier }}.json"
                },
                'loop': "{{ json_files.files }}",
                'become': False
            },
            {
                'name': 'Remove original JSON files from tmp directory',
                'local_action': {
                    'module': 'file',
                    'path': "{{ tmp_dir }}/{{ item.path | basename }}",
                    'state': 'absent'
                },
                'loop': "{{ json_files.files }}",
                'become': False
            },
            {
                'name': 'Remove script from host',
                'file': {
                    'path': "/tmp/{{ script_name }}",
                    'state': 'absent'
                }
            },
            {
                'name': 'Remove JSON files from host',
                'file': {
                    'path': "{{ item.path }}",
                    'state': 'absent'
                },
                'loop': "{{ json_files.files }}"
            }
        ]
    }]
    
    return playbook

def create_windows_playbook(group_name: str, script_name: str) -> list:
    """Create playbook for Windows systems."""
    script_path = get_script_path('Windows')
    
    playbook = [{
        'name': f'Execute {script_name} on {group_name}',
        'hosts': group_name,
        'gather_facts': True,
        'vars': {
            'script_name': script_name,
            'script_path': script_path,
            'local_dir': os.getcwd(),
            'tmp_dir': os.path.join(os.getcwd(), 'tmp')
        },
        'tasks': [
            {
                'name': 'Create tmp directory on control node',
                'local_action': {
                    'module': 'file',
                    'path': "{{ tmp_dir }}",
                    'state': 'directory'
                },
                'become': False,
                'run_once': True
            },
            {
                'name': f'Copy {script_name} to host',
                'win_copy': {
                    'src': "{{ script_path }}",
                    'dest': "C:\\temp\\{{ script_name }}"
                }
            },
            {
                'name': f'Execute {script_name}',
                'win_command': 'C:\\temp\\{{ script_name }}',
                'args': {
                    'chdir': 'C:\\temp'
                },
                'register': 'script_result'
            },
            {
                'name': 'Find generated JSON files',
                'win_find': {
                    'paths': ['C:\\temp'],
                    'patterns': ['{{ host_os_type }}_*.json']
                },
                'register': 'json_files'
            },
            {
                'name': 'Fetch JSON files to control node with original names',
                'fetch': {
                    'src': "{{ item.path }}",
                    'dest': "{{ local_dir }}/",
                    'flat': True
                },
                'loop': "{{ json_files.files }}"
            },
            {
                'name': 'Rename JSON files to use HOST_IDEN',
                'local_action': {
                    'module': 'copy',
                    'src': "{{ local_dir }}/{{ item.path | win_basename }}",
                    'dest': "{{ local_dir }}/{{ host_identifier }}.json"
                },
                'loop': "{{ json_files.files }}",
                'become': False
            },
            {
                'name': 'Remove original JSON files with IP names',
                'local_action': {
                    'module': 'file',
                    'path': "{{ local_dir }}/{{ item.path | win_basename }}",
                    'state': 'absent'
                },
                'loop': "{{ json_files.files }}",
                'become': False
            },
            {
                'name': 'Remove script from host',
                'win_file': {
                    'path': "C:\\temp\\{{ script_name }}",
                    'state': 'absent'
                }
            },
            {
                'name': 'Remove JSON files from host',
                'win_file': {
                    'path': "{{ item.path }}",
                    'state': 'absent'
                },
                'loop': "{{ json_files.files }}"
            }
        ]
    }]
    
    return playbook

def create_else_playbook(group_name: str) -> list:
    """Create a no-op playbook for 'else' OS type."""
    playbook = [{
        'name': f'No operation for {group_name} (else OS type)',
        'hosts': group_name,
        'gather_facts': False,
        'tasks': [
            {
                'name': 'Display message for unsupported OS',
                'debug': {
                    'msg': "This host has an unsupported OS type. No operations performed."
                }
            }
        ]
    }]
    
    return playbook

def create_extravars(host_list: List[Dict[str, str]]) -> dict:
    """Create extra variables for the playbook."""
    return {
        'local_dir': os.getcwd(),
        'current_time': datetime.now().strftime("%Y%m%d_%H%M%S")
    }

def check_ansible_connectivity(host_list: List[Dict[str, str]]) -> Dict[str, Dict[str, any]]:
    """
    Check if hosts are reachable and manageable by Ansible.
    Now also validates HOST_OS field.
    """
    
    # Group hosts by OS for connectivity testing
    os_groups = group_hosts_by_os(host_list)
    results = {}
    
    for os_type, hosts in os_groups.items():
        print(f"\nTesting connectivity for {os_type} hosts...")
        
        # Create inventory for this OS group
        inventory = create_os_inventory(hosts, os_type)
        group_name = f"{os_type.lower()}_hosts"
        
        # Simple connectivity test playbook
        if os_type == 'Windows':
            ping_playbook = create_windows_connectivity_playbook(group_name)
        else:
            ping_playbook = create_unix_connectivity_playbook(group_name)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                result = ansible_runner.run(
                    private_data_dir=temp_dir,
                    inventory=inventory,
                    playbook=ping_playbook,
                    quiet=True,
                    verbosity=0
                )
                
                # Process results for each host in this OS group
                for i, host in enumerate(hosts):
                    host_name = f"{os_type.lower()}_host_{i}"
                    host_iden = host['HOST_IDEN']
                    
                    results[host_iden] = {
                        'reachable': False,
                        'ssh_accessible': False,
                        'sudo_accessible': False,
                        'hostname': None,
                        'os': os_type,
                        'os_full': host.get('HOST_OS_FULL', 'N/A'),
                        'detected_os': None,
                        'error': None,
                        'host_addr': host['HOST_ADDR']  # Keep addr for display
                    }
                    
                    # Check events for this specific host
                    for event in result.events:
                        event_data = event.get('event_data', {})
                        if event_data.get('host') == host_name:
                            
                            if event.get('event') == 'runner_on_ok':
                                task_name = event_data.get('task', '')
                                res = event_data.get('res', {})
                                
                                if 'Test connection' in task_name:
                                    results[host_iden]['reachable'] = True
                                    results[host_iden]['ssh_accessible'] = True
                                    
                                elif 'Test sudo access' in task_name or 'Test admin access' in task_name:
                                    results[host_iden]['sudo_accessible'] = True
                                    
                                elif 'Gather basic system info' in task_name:
                                    facts = res.get('ansible_facts', {})
                                    results[host_iden]['hostname'] = facts.get('ansible_hostname')
                                    results[host_iden]['detected_os'] = facts.get('ansible_distribution') or facts.get('ansible_os_family')
                            
                            elif event.get('event') in ['runner_on_failed', 'runner_on_unreachable']:
                                results[host_iden]['error'] = event_data.get('res', {}).get('msg', 'Connection failed')
                
            except Exception as e:
                # If the entire run failed, mark all hosts in this group as unreachable
                for host in hosts:
                    host_iden = host['HOST_IDEN']
                    results[host_iden] = {
                        'reachable': False,
                        'ssh_accessible': False,
                        'sudo_accessible': False,
                        'hostname': None,
                        'os': os_type,
                        'os_full': host.get('HOST_OS_FULL', 'N/A'),
                        'detected_os': None,
                        'error': f'Ansible execution failed: {str(e)}',
                        'host_addr': host['HOST_ADDR']
                    }
    
    return results

def create_unix_connectivity_playbook(group_name: str) -> list:
    """Create connectivity test playbook for Unix systems."""
    return [{
        'name': 'Test Unix connectivity',
        'hosts': group_name,
        'gather_facts': False,
        'tasks': [
            {
                'name': 'Test connection',
                'ping': {},
                'register': 'ping_result'
            },
            {
                'name': 'Test sudo access',
                'command': 'whoami',
                'become': True,
                'register': 'sudo_result'
            },
            {
                'name': 'Gather basic system info',
                'setup': {
                    'filter': ['ansible_hostname', 'ansible_distribution', 'ansible_default_ipv4']
                },
                'register': 'system_info'
            }
        ]
    }]

def create_windows_connectivity_playbook(group_name: str) -> list:
    """Create connectivity test playbook for Windows systems."""
    return [{
        'name': 'Test Windows connectivity',
        'hosts': group_name,
        'gather_facts': False,
        'tasks': [
            {
                'name': 'Test connection',
                'win_ping': {},
                'register': 'ping_result'
            },
            {
                'name': 'Test admin access',
                'win_whoami': {},
                'register': 'whoami_result'
            },
            {
                'name': 'Gather basic system info',
                'setup': {
                    'filter': ['ansible_hostname', 'ansible_os_family', 'ansible_ip_addresses']
                },
                'register': 'system_info'
            }
        ]
    }]

def print_connectivity_report(connectivity_results: Dict[str, Dict[str, any]]) -> None:
    """Print a formatted connectivity report with OS information."""
    print("\n" + "="*70)
    print("ANSIBLE CONNECTIVITY REPORT")
    print("="*70)
    
    # Group results by OS
    os_groups = defaultdict(list)
    for host_iden, result in connectivity_results.items():
        os_groups[result['os']].append((host_iden, result))
    
    total_reachable = 0
    total_hosts = len(connectivity_results)
    
    for os_type, host_results in os_groups.items():
        print(f"\n{os_type.upper()} HOSTS:")
        print("-" * 50)
        
        for host_iden, result in host_results:
            print(f"\nHost ID: {host_iden} ({result['host_addr']})")
            print(f"  Full OS: {result.get('os_full', 'N/A')}")
            
            if result['reachable']:
                total_reachable += 1
                print("  ✓ Connection: SUCCESS")
                
                if result['sudo_accessible']:
                    print("  ✓ Privilege Access: SUCCESS")
                else:
                    print("  ✗ Privilege Access: FAILED")
                    
                if result['hostname']:
                    print(f"  Hostname: {result['hostname']}")
                if result['detected_os']:
                    print(f"  Detected OS: {result['detected_os']}")
                    
                # Check if declared OS matches detected OS
                if result['detected_os'] and result['os'] != 'else':
                    detected_base = extract_base_os_type(result['detected_os'])
                    declared_base = extract_base_os_type(result.get('os_full', ''))
                    if detected_base != declared_base:
                        print(f"  ⚠️  OS Mismatch: Declared as {result.get('os_full', 'Unknown')}, detected as {result['detected_os']}")
                        
            else:
                print("  ✗ Connection: FAILED")
                print("  ✗ Privilege Access: N/A")
                if result['error']:
                    print(f"  Error: {result['error']}")
    
    print("\n" + "="*70)
    print(f"SUMMARY: {total_reachable}/{total_hosts} hosts are manageable by Ansible")
    
    # Check for required scripts
    print("\nSCRIPT AVAILABILITY:")
    print("-" * 30)
    required_os_types = set(result['os'] for result in connectivity_results.values())
    for os_type in required_os_types:
        script_path = get_script_path(os_type)
        if os.path.exists(script_path):
            print(f"  ✓ {script_path}")
        else:
            print(f"  ✗ {script_path} (MISSING)")
    
    print("="*70)

def get_manageable_hosts(host_list: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Filter host list to return only hosts that are manageable by Ansible."""
    connectivity_results = check_ansible_connectivity(host_list)
    manageable_hosts = []
    
    for host in host_list:
        host_iden = host['HOST_IDEN']
        if (connectivity_results[host_iden]['reachable'] and 
            connectivity_results[host_iden]['sudo_accessible']):
            manageable_hosts.append(host)
    
    return manageable_hosts

def create_sample_scripts():
    """Create sample scripts for different OS types."""
    
    # Ubuntu script
    ubuntu_script = '''#!/bin/bash
# Ubuntu.sh - Sample script for Ubuntu systems

HOST_IP=$(hostname -I | awk '{print $1}')
JSON_FILE="/tmp/Ubuntu_${HOST_IP}.json"

# Collect system information
cat > "$JSON_FILE" << EOF
{
    "collection_time": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "hostname": "$(hostname)",
    "os": "$(lsb_release -d | cut -f2)",
    "kernel": "$(uname -r)",
    "architecture": "$(uname -m)",
    "ip_address": "$HOST_IP",
    "uptime": "$(uptime -p)",
    "memory_total": "$(free -h | awk '/^Mem:/ {print $2}')",
    "disk_usage": "$(df -h / | awk 'NR==2 {print $5}')",
    "cpu_cores": "$(nproc)",
    "load_average": "$(uptime | awk -F'load average:' '{print $2}')"
}
EOF

echo "Ubuntu system information collected in $JSON_FILE"
'''
    
    # CentOS script
    centos_script = '''#!/bin/bash
# CentOS.sh - Sample script for CentOS/RHEL systems

HOST_IP=$(hostname -I | awk '{print $1}')
JSON_FILE="/tmp/CentOS_${HOST_IP}.json"

# Collect system information
cat > "$JSON_FILE" << EOF
{
    "collection_time": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "hostname": "$(hostname)",
    "os": "$(cat /etc/redhat-release)",
    "kernel": "$(uname -r)",
    "architecture": "$(uname -m)",
    "ip_address": "$HOST_IP",
    "uptime": "$(uptime -p)",
    "memory_total": "$(free -h | awk '/^Mem:/ {print $2}')",
    "disk_usage": "$(df -h / | awk 'NR==2 {print $5}')",
    "cpu_cores": "$(nproc)",
    "load_average": "$(uptime | awk -F'load average:' '{print $2}')"
}
EOF

echo "CentOS system information collected in $JSON_FILE"
'''
    
    # Windows script
    windows_script = '''@echo off
REM Windows.bat - Sample script for Windows systems

for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr "IPv4"') do set HOST_IP=%%a
set HOST_IP=%HOST_IP: =%
set JSON_FILE=C:\\temp\\Windows_%HOST_IP%.json

(
echo {
echo   "collection_time": "%date% %time%",
echo   "hostname": "%COMPUTERNAME%",
echo   "os": "%OS%",
echo   "architecture": "%PROCESSOR_ARCHITECTURE%",
echo   "ip_address": "%HOST_IP%",
echo   "user": "%USERNAME%",
echo   "domain": "%USERDOMAIN%"
echo }
) > "%JSON_FILE%"

echo Windows system information collected in %JSON_FILE%
'''
    
    # Else script (no-op)
    else_script = '''#!/bin/bash
# else.sh - No-op script for unsupported OS types

echo "This OS type is not supported. No operations performed."
exit 0
'''
    
    # Write scripts to current directory
    scripts = {
        'script/Ubuntu/Ubuntu_cce.sh': ubuntu_script,
        'script/CentOS/CentOS_cce.sh': centos_script,
        'script/Windows/Windows_cce.bat': windows_script,
        'script/else/else_cce.sh': else_script
    }
    
    for script_path, script_content in scripts.items():
        full_script_path = os.path.join(os.getcwd(), script_path)
        
        # Create directory if it doesn't exist
        script_dir = os.path.dirname(full_script_path)
        os.makedirs(script_dir, exist_ok=True)
        
        if not os.path.exists(full_script_path):
            with open(full_script_path, 'w') as f:
                f.write(script_content)
            
            # Make Unix scripts executable
            if script_path.endswith('.sh'):
                os.chmod(full_script_path, 0o755)
            
            print(f"Created sample script: {full_script_path}")
        else:
            print(f"Script already exists: {full_script_path}")

# Example usage
if __name__ == "__main__":
    # Create sample scripts if they don't exist
    print("Checking for required scripts...")
    create_sample_scripts()
    
    # Example host list with OS and identifier information
    hosts = [
        {
            'HOST_IDEN': 1,
            'HOST_ADDR': '192.168.200.227',
            'HOST_USER': 'ubuntu',
            'HOST_PORT': '2020',
            'HOST_SUPW': '0630',
            'HOST_OS': 'Ubuntu 24.04'
        },
        {
            'HOST_IDEN': 2,
            'HOST_ADDR': '192.168.200.227', 
            'HOST_USER': 'centos',
            'HOST_PORT': '2021',
            'HOST_SUPW': '20250630!',
            'HOST_OS': 'CentOS 8.5'
        },
        {
            'HOST_IDEN': 3,
            'HOST_ADDR': '192.168.1.102',
            'HOST_USER': 'Administrator',
            'HOST_PORT': '5985',  # WinRM port
            'HOST_SUPW': 'windows_password',
            'HOST_OS': 'Windows Server 2019'
        },
        {
            'HOST_IDEN': 4,
            'HOST_ADDR': '192.168.1.103',
            'HOST_USER': 'root',
            'HOST_PORT': '22',
            'HOST_SUPW': 'root_password',
            'HOST_OS': 'Red Hat Enterprise Linux 9.2'
        }
    ]
    
    # First, check connectivity to all hosts
    print("\nChecking Ansible connectivity...")
    connectivity_results = check_ansible_connectivity(hosts)
    print_connectivity_report(connectivity_results)
    
    # Get only manageable hosts
    manageable_hosts = get_manageable_hosts(hosts)
    
    if manageable_hosts:
        print(f"\nProceeding with {len(manageable_hosts)} manageable hosts...")
        success = run_ansible_playbook_on_hosts(manageable_hosts)
        
        if success:
            print("\nJSON files should now be in your tmp directory!")
            print("Check for files like: tmp/1.json, tmp/2.json, tmp/3.json, tmp/4.json")
        else:
            print("Failed to execute playbook on some hosts.")
    else:
        print("NOTHING TO DO")