import subprocess
import os

command = "zowe zos-files download ds Z58582.SYSINFO"
sysinfo_file_path = "z58582/sysinfo.txt"

def check_age_file(file_path):
    if os.path.exists(file_path):
        age_file = os.path.getmtime(file_path)

        if age_file > 3600:
            subprocess(command, )
    

check_age_file(sysinfo_file_path)