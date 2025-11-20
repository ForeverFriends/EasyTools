# -*- coding: utf-8 -*-

import subprocess
import sys
import time
import os

def run_command(cmd):
    """运行命令并返回输出，出错时抛出异常"""
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {' '.join(cmd)}")
        print(f"错误信息: {e.stderr.strip()}")
        return None

def is_device_connected(target_device):
    """检查特定设备是否已连接"""
    output = run_command(["adb", "devices"])
    if output:
        lines = output.splitlines()
        for line in lines[1:]:
            if target_device in line and "device" in line:
                return True
    return False

def wait_for_any_device(check_interval=3):
    """不断检测是否有任何 adb 设备连接"""
    print("🔍 正在等待 adb 设备连接 (按 Ctrl+C 退出)...")
    try:
        while True:
            output = run_command(["adb", "devices"])
            if output:
                lines = output.splitlines()
                devices = [line for line in lines[1:] if line.strip() and "device" in line]
                if devices:
                    print(f"✅ 检测到 {len(devices)} 个设备！")
                    break
            #  print(f"⏳ 没有检测到设备，{check_interval} 秒后重试...")
            time.sleep(check_interval)
    except KeyboardInterrupt:
        print("\n👋 检测被用户取消，退出程序。")
        sys.exit(0)

def wait_for_specific_device(target_device, timeout=10, check_interval=1):
    """等待特定的设备上线"""
    print(f"🔍 正在等待设备 {target_device} 出现...")
    start_time = time.time()
    try:
        while True:
            if is_device_connected(target_device):
                #  print(f"✅ 设备 {target_device} 已连接！")
                return None
            if time.time() - start_time > timeout:
                #  print(f"❌ 超时 {timeout} 秒，设备 {target_device} 仍未连接。")
                return TimeoutError
            #  print(f"⏳ 设备未就绪，{check_interval} 秒后重试...")
            time.sleep(check_interval)
    except KeyboardInterrupt:
        print("\n👋 检测被用户取消，退出程序。")
        sys.exit(0)

def setup_ports():
    port_mappings = [
        (8855, 6665),
        (8877, 6667),
        (8866, 6666),
    ]

    # 检查已有的 adb forward
    forward_output = run_command(["adb", "forward", "--list"])
    existing_forwards = set()
    if forward_output:
        lines = forward_output.splitlines()
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 3:
                existing_forwards.add((parts[1], parts[2]))

    # 执行 adb forward（只打印新增）
    for local_port, remote_port in port_mappings:
        local_str = f"tcp:{local_port}"
        remote_str = f"tcp:{remote_port}"
        if (local_str, remote_str) not in existing_forwards:
            cmd_forward = ["adb", "forward", local_str, remote_str]
            result = run_command(cmd_forward)
            if result is not None:
                print(f"✅ 端口转发成功: {local_port} -> {remote_port}")

    # 连接设备（多次重试）
    MAX_RETRIES = 3
    RETRY_INTERVAL = 2  # 秒

    for local_port, _ in port_mappings:
        device_id = f"127.0.0.1:{local_port}"

        success = False
        for attempt in range(1, MAX_RETRIES + 1):
            # 检查当前连接状态
            devices_output = run_command(["adb", "devices"])
            connected_devices = set()
            if devices_output:
                lines = devices_output.splitlines()[1:]  # 跳过 header
                for line in lines:
                    device_info = line.strip().split('\t')
                    if len(device_info) >= 2 and device_info[1] == 'device':
                        connected_devices.add(device_info[0])

            if device_id in connected_devices:
                success = True
                #  if attempt == 1:
                    #  print(f"✅ 设备 {device_id} 已连接。")
                break  # 已连接则直接退出循环

            # 尝试连接
            cmd_connect = ["adb", "connect", device_id]
            result = run_command(cmd_connect)
            #  if result is not None:
                #  print(f"🔄 第 {attempt} 次尝试连接 {device_id} ...")

            time.sleep(RETRY_INTERVAL)

        # 最终状态
        if not success:
            print(f"⚠️ 设备 {device_id} 连接失败，请检查设备或重启 adb。")
        #  else:
        #      print(f"✅ 设备连接成功: {device_id}")

    print("🎉 端口转发和设备连接检查完成！")

def connect_to_all_devices():
    try:
        # print("👉 检查是否有任何 adb 设备...")
        wait_for_any_device()
        print("👉 config adb port...")

        # yocto
        if run_command(["adb", "forward", "tcp:8855", "tcp:6665"]) is None:
            sys.exit(1)
        # Android
        if run_command(["adb", "forward", "tcp:8866", "tcp:6666"]) is None:
            sys.exit(1)
        # tbox
        if run_command(["adb", "forward", "tcp:8877", "tcp:6667"]) is None:
            sys.exit(1)

        connect_output = run_command(["adb", "connect", "127.0.0.1:8877"])
        if not connect_output or "connected" not in connect_output.lower():
            print("❌ adb connect 失败！输出信息：", connect_output)
            sys.exit(1)

        connect_output = run_command(["adb", "connect", "127.0.0.1:8866"])
        if not connect_output or "connected" not in connect_output.lower():
            print("❌ adb connect 失败！输出信息：", connect_output)
            sys.exit(1)

        connect_output = run_command(["adb", "connect", "127.0.0.1:8855"])
        if not connect_output or "connected" not in connect_output.lower():
            print("❌ adb connect 失败！输出信息：", connect_output)
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 检测被用户取消，退出程序。")
        sys.exit(0)

def connect_to_device():
    try:
        # print("👉 检查是否有任何 adb 设备...")
        wait_for_any_device()
        print("👉 config adb port...")
        while True:
            #  print("👉 执行端口转发...")
            if run_command(["adb", "forward", "tcp:8855", "tcp:6665"]) is None:
                sys.exit(1)

            if run_command(["adb", "forward", "tcp:8877", "tcp:6667"]) is None:
                sys.exit(1)
            #  print("✅ 端口转发成功: tcp:8855 -> tcp:6665")

            #  print("👉 连接到 127.0.0.1:8855...")
            connect_output = run_command(["adb", "connect", "127.0.0.1:8877"])
            if not connect_output or "connected" not in connect_output.lower():
                print("❌ adb connect 失败！输出信息：", connect_output)
                sys.exit(1)

            connect_output = run_command(["adb", "connect", "127.0.0.1:8855"])
            if not connect_output or "connected" not in connect_output.lower():
                print("❌ adb connect 失败！输出信息：", connect_output)
                sys.exit(1)
            #  print("✅ 成功发送 adb connect 命令")

            # 等待设备上线
            if wait_for_specific_device(target_device, timeout=10, check_interval=1) is None:
                return
    except KeyboardInterrupt:
        print("\n👋 检测被用户取消，退出程序。")
        sys.exit(0)

def list_connected_devices():
    output = run_command(["adb", "devices"])
    devices = []
    if output:
        lines = output.splitlines()[1:]  # Skip the header line
        for line in lines:
            parts = line.strip().split('\t')
            if len(parts) == 2 and parts[1] == 'device':
                devices.append(parts[0])
    return devices

def execute_push(target_device, local_path, remote_path):
    if not os.path.exists(local_path):
        print("❌ 本地文件不存在: {}".format(local_path))
        sys.exit(1)
    run_command(["adb", "-s", target_device, "shell", "mount", "-o", "remount,rw", "/"])
    print("📤 正在 push 文件: {} → {}".format(local_path, remote_path))
    cmd = ["adb", "-s", target_device, "push", local_path, remote_path]
    result = run_command(cmd)
    if result:
        print("✅ push 成功！输出如下：")
        print(result)
    else:
        print("❌ push 操作失败！")

def execute_pull(target_device, remote_path, local_path):
    print("📥 正在 pull 文件: {} → {}".format(remote_path, local_path))
    cmd = ["adb", "-s", target_device, "pull", remote_path, local_path]
    result = run_command(cmd)
    if result:
        print("✅ pull 成功！输出如下：")
        print(result)
    else:
        print("❌ pull 操作失败！")

def choose_device():
    devices = list_connected_devices()
    if not devices:
        print("❌ 没有检测到任何可用设备，请检查设备连接并确保 adb 已启动。")
        sys.exit(1)

    # 定义 IP 和别名的映射
    device_aliases = {
        "127.0.0.1:8855": "yocto",
        "127.0.0.1:8866": "android",
        "127.0.0.1:8877": "tbox",
        # 这里可以添加更多映射
    }

    print("📱 检测到以下可用设备：")
    for idx, device in enumerate(devices, start=1):
        alias = device_aliases.get(device, "")
        if alias:
            print("  {}. {} ({})".format(idx, device, alias))
        else:
            print("  {}. {}".format(idx, device))

    while True:
        try:
            choice = input("请输入要选择的设备编号（默认 1，Ctrl+C 退出）：").strip()
            if choice == "":
                return devices[0]
            elif choice.isdigit() and 1 <= int(choice) <= len(devices):
                return devices[int(choice)-1]
            else:
                print("⚠️ 输入无效，请重新输入。")
        except KeyboardInterrupt:
            print("\n👋 用户取消选择，退出脚本。")
            sys.exit(0)

def run_command(cmd):
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print("❌ 命令执行失败: {}".format(' '.join(cmd)))
        print("错误信息: {}".format(e.stderr.strip()))
        return None

def execute_shell_command(target_device, shell_cmd):
    print("👉 执行 adb shell 命令: {}".format(shell_cmd))
    try:
        full_cmd = ["adb", "-s", target_device, "shell"] + shell_cmd.split()
        output = run_command(full_cmd)
        if output:
            print("\n====== 命令输出结果 ======")
            print(output)
            print("======= 输出结束 =========\n")
        else:
            print("⚠️ 命令无输出或执行失败")
    except Exception as e:
        print("❌ 执行 shell 命令出错: {}".format(e))
        sys.exit(1)

def main():
    print(f"👉 ydb start...")
    arg_no_used = 0
    device_name = "android"
    wait_for_any_device()
    try:
        setup_ports()
        #  target_device = "127.0.0.1:8866"
        #  if is_device_connected(target_device) is False:
        #      connect_to_all_devices();

        if len(sys.argv) < 2:
            target_device = choose_device()
            subprocess.run(["adb", "-s", target_device, "shell"])
            if is_device_connected(target_device) is False:
                print("👉 进入 {} shell...".format(target_device))
                subprocess.run(["adb", "-s", target_device, "shell"])
            return 0
        else:
            args = sys.argv[1:]
            if args[0] == "a":
                target_device = "127.0.0.1:8866";
                device_name = "android"
            elif args[0] == "y":
                target_device = "127.0.0.1:8855";
                device_name = "yocto"
            elif args[0] == "t":
                target_device = "127.0.0.1:8877";
                device_name = "tbox"
            else:
                arg_no_used = 1
                target_device = choose_device()

            if arg_no_used == 1:
                user_input = args[0:]
            elif len(args) > 2:
                user_input = args[1:]
            else:
                print("👉 进入 {} shell...".format(device_name))
                subprocess.run(["adb", "-s", target_device, "shell"])
                return None

        if user_input[0] == "push":
            if len(user_input) != 3:
                print("❌ push 用法错误。示例：ydb push ./file.txt /data/local/tmp/")
                sys.exit(1)
            execute_push(target_device, user_input[1], user_input[2])
        elif user_input[0] == "pull":
            if len(user_input) != 3:
                print("❌ pull 用法错误。示例：ydb pull /data/file.txt ./local_file.txt")
                sys.exit(1)
            execute_pull(target_device, user_input[1], user_input[2])
        else:
            subprocess.run(["adb", "-s", target_device, "shell"])
    except KeyboardInterrupt:
        print("\n👋 已退出 shell 会话")
    except Exception as e:
        print(f"❌ 打开 shell 出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

