import re
import subprocess
from pathlib import Path
import sys
import platform
from typing import Optional
from enum import Enum

class System(Enum):
    WINDOWS=0
    LINUX=1

platform: str = platform.system().lower()

system: Optional[System] = None

os_shell: list[str] = []

if "lin" in platform:
    system = System.LINUX
    os_shell = ["bash", "-c"]
elif "darwin" in platform:
    pass
elif "win" in platform:
    system = System.WINDOWS
    os_shell = ["powershell", "-Command"]

home_dir: str = Path.home()

if not home_dir:
    sys.exit("Cannot detect the home directory.")

if not system:
    sys.exit("Cannot detect OS.")

PROMPT: str = "$: "

def pprint(msg: str):
    print(f"{msg}\n{PROMPT}")

def handle_subprocess(cmd: list[str]) -> Optional[str]:
    process_result: subprocess.CompletedProcess = subprocess.run(cmd, capture_output=True)
    if process_result.returncode != 0:
        raise Exception(f"An error occured: {cmd.stderr}")
    else:
        return process_result.stdout.decode('utf-8')

vm_name: str = ""

if len(sys.argv) > 1:
    vm_name = sys.argv[1]
else:
    print("Welcome to the ssh_config updater.")

available_vms_stdout: str = handle_subprocess(os_shell + ["VBoxManage list vms"])
available_vms: list[str] = re.findall(r"(\S+)\s+\S+", available_vms_stdout)
available_vms_cleaned = [vm.strip("\" ").lower() for vm in available_vms]

if not available_vms:
    sys.exit("No VMs found. Exiting...")

while True:

    print(f"Found VMs on HOST: {available_vms}")

    if not vm_name:
        vm_name: str = input(f"Name of the VM\n{PROMPT}")

    if vm_name == "":
        print(f"Empty VM name.")
        print("Try again.")
        continue

    try:
        str(vm_name)
    except ValueError as e:
        print(f"Wrong input, the vm name cannot be converted into a str: ({vm_name}) | ({e})")
        print("Try again.")
        vm_name = ""
        continue

    if vm_name.lower() not in available_vms_cleaned:
        print(f"VM name ({vm_name}) not in ({available_vms})")
        print("Try again.")
        vm_name = ""
        continue

    vbox_ip_stdout = handle_subprocess(os_shell + [f"VBoxManage guestproperty enumerate {vm_name} | findstr /i ip"])
    if ((main_ip_match := re.match(r".*?/Net/0/.*?value:\s+(?P<IP>\d+\.\d+\.\d+\.\d+)", vbox_ip_stdout, flags=re.IGNORECASE)) 
        and main_ip_match.group("IP")
        ):
        vm_ip: str = main_ip_match.group("IP")
        if not vm_ip:
            print(f"VM IP not found!")
            print("Try again.")
            vm_name = ""
            continue
        
        ssh_config_path: Path = Path(rf"{home_dir}\.ssh\config")
        ssh_config_updated: str = ""
        with ssh_config_path.open(mode="r+") as ssh_config_file:
            ssh_config: str = ssh_config_file.read()
            
            vm_config_pattern = re.compile(rf".*?(?P<VMConfig>^host {vm_name}.*?^(?!\s+))", re.DOTALL | re.IGNORECASE | re.MULTILINE)
            if ((vm_config_slice_match := vm_config_pattern.match(ssh_config))
                and vm_config_slice_match.group("VMConfig")
                ):
                
                vm_config_slice: str = vm_config_slice_match.group("VMConfig")

                hostname_pattern: re.Pattern = re.compile(r"hostname\s+(\d+\.\d+\.\d+\.\d+)", flags=re.IGNORECASE)
                current_vm_ip: str = ""
                if ((current_vm_ip_match := hostname_pattern.search(vm_config_slice))
                    and current_vm_ip_match.group(1)
                    ):
                    current_vm_ip = current_vm_ip_match.group(1)

                if current_vm_ip and vm_ip and current_vm_ip == vm_ip:
                    print(f"The {vm_name}\'s config seems to be up-to-date with ip: {current_vm_ip}")
                    break

                vm_config_slice_updated: str = hostname_pattern.sub(f"HostName {vm_ip}", vm_config_slice)

                if vm_config_slice == vm_config_slice_updated:
                    raise("Error. No update performed.")

                ssh_config_updated = ssh_config.replace(vm_config_slice, vm_config_slice_updated)
            else:
                print(f"No config found for vm: {vm_name}")
                print("Try again.")
                vm_name = ""
                continue
        with ssh_config_path.open(mode="w") as ssh_config_file:
            if ssh_config_updated:
                ssh_config_file.write(ssh_config_updated)
                print(f"Update successful. {vm_name}\' ip is now: {vm_ip}")
                break
            else:
                print("Update unsuccessful.")
    else:
        print(f"No IP found for vm: {vm_name}")
        print("Try again.")
        vm_name = ""
        continue
