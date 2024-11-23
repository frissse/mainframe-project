import subprocess
import os

command = "zowe zos-files download ds Z58582.SYSINFO"
sysinfo_file_path = "z58582/sysinfo.txt"

def download_sysfile(file_path):
    if os.path.exists(file_path):
        print("file exists")
    else:
        print(f"file in ${sysinfo_file_path} not found, downloading")
        subprocess.run(command, shell=True, capture_output=True)
    

check_age_file(sysinfo_file_path)