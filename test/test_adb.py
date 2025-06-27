import subprocess
qnx_ip = "192.168.1.1"
hosts_content = subprocess.check_output(['adb', 'shell', 'cat', '/etc/hosts']).decode('utf-8')

lines = hosts_content.split('\n')

for line in lines:
    if "cdc-qnx" in line:
        parts = line.split()
        if parts:
            qnx_ip = parts[0]


print(qnx_ip)

