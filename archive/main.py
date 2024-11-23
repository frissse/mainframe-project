import os
import sys
import json
from zoautil_py import zsystem, datasets
import platform
import subprocess

USERID = os.getenv('USER')
output_dataset = USERID+".SYSINFO"
sysinfo = {}

def get_sysinfo():
    try:
        # add latest logs
        # add 4 latest used command in history
        uptime = subprocess.run(["uptime"], capture_output=True, text=True)
        os_name = platform.system()
        os_version = platform.release()
        cpu_info = json.loads(zsystem.zinfo(['cpu']))
        cpu_type = cpu_info['cpu_info']['cpc_nd_type']
        cpu_manufacturer = cpu_info['cpu_info']['cpc_nd_manufacturer']
    except:
        print("error occured getting sysinfo")

    sysinfo.update({"uptime": uptime.stdout,
        "os_name": os_name,
        "os_version": os_version,
        "cpu_type": cpu_type,
        "cpu_manufacturer": cpu_manufacturer})
    

def parse_freediskspace():
    command = "df -kP | awk '$5+0 > 90 {print $1, $5}'"
    fds_over90 = subprocess.run(command, shell=True, capture_output=True, text=True)

    if fds_over90.returncode == 0:
        lines = fds_over90.stdout.splitlines()
        filesystem_data = []

        # Process each line of the output
        for line in lines:
            # Split each line into filesystem and capacity
            filesystem, capacity = line.split()
            # Add the data to the dictionary in a structured format
            filesystem_data.append({
                "filesystem": filesystem,
                "capacity": capacity
            })

        # Display the dictionary (this can later be used in a Flask dashboard)
        sysinfo["filesystems"] = filesystem_data
    else:
        print(f"Error: {fds_over90.stderr}")

def parse_running_processes():
    command = "ps -ef | awk '{print $2, $8}'"
    running_processes = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    process_info = []

    if running_processes.returncode == 0:
        # Split the command output into lines
        lines = running_processes.stdout.splitlines()

        # Skip the header line and process each subsequent line
        for line in lines[1:]:
            # Split the line into fields by whitespace
            fields = line.split() 
            pid = fields[0]  
            cmd = fields[1]
            process_info.append({"PID": pid, "CMD": cmd})
        
        sysinfo["processes"] = process_info
    else:
        print(f"Error: {running_processes.stderr}")

def parse_log():
    command = "cat /etc/log | tail -n 5"
    log = subprocess.run(command, shell=True, capture_output=True, text=True)

    if log.returncode == 0:
        sysinfo['log'] = log.stdout
    else:
        print(f"Error: {log.stderr}")

def write_dataset():
    if datasets.exists(output_dataset):
        datasets.delete(output_dataset)
    
    info_string = f"""uptime: {sysinfo['uptime'].strip()}
    os_name: {sysinfo['os_name']}
    os_version: {sysinfo['os_version']}
    cpu_type: {sysinfo['cpu_type']}
    cpu_manufacturer: {sysinfo['cpu_manufacturer']}
    free disk space: {sysinfo['filesystems']}
    running processes: {sysinfo['processes']}
    last_log_message: {sysinfo['log']}
    history_command: {sysinfo['history']}
    """
    print(info_string)

    datasets.write(output_dataset, info_string, dataset_type="SEQ")

if __name__ == "__main__":
    get_sysinfo()
    parse_freediskspace()
    parse_running_processes()
    parse_log()
    write_dataset()