import subprocess
import os
import csv
from datetime import datetime

formatted_date = ""

def get_zos_id():
    # check for file named zos_id.txt
    if os.path.exists("zos_id.txt"):
        with open("zos_id.txt", mode='r') as file:
            zos_id = file.read()
            return zos_id
    zos_id = input("Enter your z/OS ID: ")
    # write the zos_id to a file
    with open("zos_id.txt", mode='w') as file:
        file.write(zos_id)
    return zos_id

zos_id = get_zos_id()

def copy_rexx_file():
    list_command = f"zowe zos-files list ds {zos_id}.SCRIPTS.* -a"
    list_ds = subprocess.run(list_command, shell=True, capture_output=True)
    str_stdout = list_ds.stdout.decode('utf-8')
    
    if (f"{zos_id}.SCRIPTS.AVGREXX" in str_stdout and f"{zos_id}.SCRIPTS.SUMREXX" in str_stdout):
        print("REXX files already present on mainframe.")
        return 0
    else:
        create_rexx_ds_avg = subprocess.run(f"zowe zos-files create ds {zos_id}.SCRIPTS.AVGREXX --record-format FB --record-length 80 --block-size 800", shell=True, capture_output=True)
        create_rexx_ds_sum = subprocess.run(f"zowe zos-files create ds {zos_id}.SCRIPTS.SUMREXX --record-format FB --record-length 80 --block-size 800", shell=True, capture_output=True)
        copy_command_rexx_avg = subprocess.run(f"zowe zos-files upload file-to-data-set \"AVGREXX\" \"Z58582.SCRIPTS.AVGREXX\"", shell=True, capture_output=True)
        copy_command_rexx_sum = subprocess.run(f"zowe zos-files upload file-to-data-set \"SUMREXX\" \"Z58582.SCRIPTS.SUMREXX\"", shell=True, capture_output=True)
        
        if "ERROR" not in copy_command_rexx_avg.stdout.decode('UTF-8') and "ERROR" not in copy_command_rexx_sum.stdout.decode('UTF-8'):
            print("REXX files copied successfully.")
            return 0
        else:
            print("Error copying REXX files.")
            return 1

print(f"\nWelcome to zMoneyTracker {zos_id}!")
print("This program allows you to input your expenses and get insights on them.")
print("the expenses are stored in a mainframe dataset.")
print("we suggest you enter the expenses for a specific month and year.")
print("but it might also be an option to create a file per category.")

def get_input_id():
    id = input("Enter the id of the file: ")
    return id

def get_formatted_date():
    date = input("Enter the date to be used as suffix for the file in format YYYY-MM: ")
    date_object = datetime.strptime(date, "%Y-%m")
    global formatted_date 
    formatted_date = date_object.strftime("%y%m")

def menu():
    while True:
        
        print("\nWhat do you want to do?")
        print("1. Enter expense (manual or by file)")
        print("2. List files")
        print("3. Get expense insights")
        print("4. Merge files")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ")

        if choice == '1':
            input_expenses()
        elif choice == '2':
            get_files()
        elif choice == '3':
            get_expense_insights()
        elif choice == '4':
            merge_files()
            break
        elif choice == '5':
            print("Exiting the menu. Goodbye!")
            break
        else:
            print("Invalid choice, please try again.")

def input_expenses():
    while True:
        print("\nHow do you want to input the expenses?")
        print("1. From CSV file")
        print("2. Manually")
        print("3. Exit")

        choice = input("Enter your choice (1-3): ")

        if choice == '1':
            input_expenses_from_csv()
        elif choice == '2':
            input_expenses_manual()
        elif choice == '3':
            print("Exiting the menu. Goodbye!")
            break
        else:
            print("Invalid choice, please try again.")

def input_expenses_from_csv():
    get_formatted_date()
    file = input("Enter the file path of the CSV file:")
    csv_file = ""
    with open(file, mode='r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)
        for row in csv_reader:
            date = row[0]
            amount = row[1]
            category = row[2]
            print(f"Date: {date}, Amount: {amount}, Category: {category}")
        
        # rename the inputted file to expenses-formatted_date.csv
        csv_file = f'expenses-E{formatted_date}.csv'
        
    os.rename(file.name, csv_file)
        
    clean_up_file(formatted_date)   
        
    upload_expenses_to_ds(csv_file)

    
def input_expenses_manual():
    get_formatted_date()
    csv_file = f'expenses-{formatted_date}.csv'

    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)

        while True:
            date = input("Enter the date (YYYY-MM-DD): ")

            amount = float(input("Enter the amount: "))
            category = input("Enter the expense category: ")

            # Write the current expense entry to the CSV file
            writer.writerow([date, amount, category])

            more = input("Would you like to add another expense? (y/n): ")
            if more.lower() != 'y':
                break

    upload_expenses_to_ds(csv_file)


def upload_expenses_to_ds(csv_file):
    list_command = f"zowe zos-files list ds {zos_id}.EXPENSES.E{formatted_date} -a"
    create_command = f"zowe zos-files create ds {zos_id}.EXPENSES.E{formatted_date} --record-format FB --record-length 80 --block-size 800"
    create_command_copy = f"zowe zos-files create ds {zos_id}.EXPENSES.E{formatted_date}.COPY --record-format FB --record-length 80 --block-size 800"
    delete_command = f"zowe zos-files delete ds {zos_id}.EXPENSES.E{formatted_date} -f"
    upload_command = f"zowe zos-files upload file-to-data-set \"{csv_file}\" \"{zos_id}.EXPENSES.E{formatted_date}\""
    upload_command_copy = f"zowe zos-files upload file-to-data-set \"{csv_file}\" \"{zos_id}.EXPENSES.E{formatted_date}.COPY\""

    list_ds = subprocess.run(list_command, shell=True, capture_output=True)
    str_stdout = list_ds.stdout.decode('utf-8')
    
    if (f"{zos_id}.EXPENSES.E{formatted_date}" in str_stdout):
        print("File already exists.")
        print("Do you want to overwrite the file?")
        overwrite = input("Enter y/n: ")
        if overwrite.lower() == 'y':
            delete_ds = subprocess.run(delete_command, shell=True, capture_output=True)
            print(delete_ds.stdout.decode('utf-8'))
            create_ds = subprocess.run(create_command, shell=True, capture_output=True)
            upload_command = subprocess.run(upload_command, shell=True, capture_output=True)
            print(create_ds.stdout.decode('utf-8'))
        else:
            create_copy_ds = subprocess.run(create_command_copy, shell=True, capture_output=True)
            upload_copy_ds = subprocess.run(upload_command_copy, shell=True, capture_output=True)
            print(create_copy_ds.stdout.decode('utf-8'))
            merge_files("auto", f"{formatted_date}", f"{formatted_date}.COPY")
            return 0        

        return 0
        

    create_ds = subprocess.run(create_command, shell=True, capture_output=True)
    print(create_ds.stdout.decode('utf-8'))
    upload_ds = subprocess.run(upload_command, shell=True, capture_output=True)
    print(upload_ds.stdout.decode('utf-8'))

def get_files():
    # TODO: list all or specific file
    # TODO: download the file, convert to csv
    while True:
        print("\nWhat do you want to do?")
        print("1. List all files")
        print("2. List specific file")
        print("3. Exit")

        choice = input("Enter your choice (1-3): ")

        if choice == '1':
            list_all_files()
        elif choice == '2':
            list_specific_file()
        elif choice == '3':
            print("Exiting the menu. Goodbye!")
            break
        else:
            print("Invalid choice, please try again.")

def download_file(id):
    download_command = f"zowe zos-files download data-set {zos_id}.EXPENSES.E{id} -f expenses-E{id}.csv"
    download_ds = subprocess.run(download_command, shell=True, capture_output=True)

def clean_up_file(id):
    with open(f"expenses-E{id}.csv", mode='r') as file:
        lines = file.readlines()

    with open(f"expenses-E{id}.csv", mode='w') as file:
        substring = "Date"
        for line in lines:
            if substring not in line:
                file.write(line)

def list_all_files():
    list_command = "zowe zos-files list ds {zos_id}.EXPENSES.E* -a"
    list_ds = subprocess.run(list_command, shell=True, capture_output=True)
    result = list_ds.stdout.decode('utf-8')
    parse_list_output(result)

def list_specific_file(id=None):
    list_command = f"zowe zos-files list ds {zos_id}.EXPENSES.E{id} -a"
    list_ds = subprocess.run(list_command, shell=True, capture_output=True)
    result = list_ds.stdout.decode('utf-8')

    print(result)

    if (f"{zos_id}.EXPENSES.E{id}" not in result):
        print("File not found.")
        return 1
    else:
        parse_list_output(result, id)
        return 0

def parse_list_output(result, id=None):
    if id is not None:
        matching_lines = [line for line in result.splitlines() if id in line]
        print("found the following files:")
        count = 0
        for line in matching_lines:
            result = line.split(":")[1]
            count += 1
            print(f"{count}", result)
            
    else:
        matching_lines = [line for line in result.splitlines() if "dsname:" in line]
        print("found the following files:")
        count = 0
        for line in matching_lines:
            result = line.split(":")[1]
            count += 1
            print(f"{count}", result)

    return 0


def merge_files(mode=None, id1=None, id2=None):
    merge_job_command = "zowe zos-jobs submit local-file \"MERGE_JOB.txt\""

    if mode != "auto":
        id1 = get_input_id()
        id2 = get_input_id()
    
    print(id1)
    print(id2)
    
    id_merged = get_input_id()
    
    id1_present = list_specific_file(id1)
    id2_present = list_specific_file(id2)

    if id1_present == 1:
        print(f"File with id {id1} not found.")
        return 1
    
    if id2_present == 1:
        print(f"File with id {id2} not found.")
        return 1
    
    if id1_present == 0 and id2_present == 0:
        create_merge_job(id1, id2, id_merged)
        merge_command = subprocess.run(merge_job_command, shell=True, capture_output=True)
        print(merge_command.stdout.decode('utf-8'))
        
def create_merge_job(id1,id2, id_merged):
    output_file = "MERGE_JOB.txt"

    jcl_content = f"""//MERGEJOB JOB
//STEP1    EXEC PGM=SORT
//SORTIN   DD DISP=SHR,DSN={zos_id}.EXPENSES.E{id1}
//         DD DISP=SHR,DSN={zos_id}.EXPENSES.E{id2}
//SORTOUT  DD DSN={zos_id}.EXPENSES.E{id_merged},
//         DISP=(NEW,CATLG,DELETE),
//         SPACE=(CYL,(1,1),RLSE),
//         DCB=(RECFM=FB,LRECL=80) 
//SYSOUT   DD SYSOUT=*
//SYSIN    DD *
  SORT FIELDS=COPY
/* 
"""

    # Write the JCL to a file
    with open(output_file, "w") as f:
        f.write(jcl_content) 

def get_expense_insights():
    while True:
        print("\nWhat do you want to do?")
        print("1. Get total expense")
        print("2. Get average expense")
        print("3. Get expense by category")
        print("4. Exit")

        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            get_total()
        elif choice == '2':
            get_average()
        elif choice == '3':
            get_by_category()
        elif choice == '4':
            print("Exiting the menu. Goodbye!")
            break
        else:
            print("Invalid choice, please try again.")

def get_total():
    id = get_input_id()
    calc = "SUM"
    command = f"zowe zos-tso issue command \"exec '{zos_id}.SCRIPTS.{calc}REXX' 'EXPENSES.E{id}'\""
    get_sum = subprocess.run(command, shell=True, capture_output=True) 
    print(get_sum.stdout.decode('utf-8'))
    # download_file(id)

    # with open(f"expenses-E{id}.csv", mode='r') as file:
    #     csv_reader = csv.reader(file)
    #     next(csv_reader)
    #     total = 0
    #     for row in csv_reader:
    #         total += float(row[1])
    #     print(f"The total expense is: {total}")
    # return 0


def get_average():
    id = get_input_id()
    print(id)
    calc = "AVG"
    command = f"zowe zos-tso issue command \"exec '{zos_id}.SCRIPTS.{calc}REXX' 'EXPENSES.E{id}'\""
    get_average = subprocess.run(command, shell=True, capture_output=True)
    print(get_average.stdout.decode('utf-8'))
    # download_file(id)

    # with open(f"expenses-{id}.csv", mode='r') as file:
    #     csv_reader = csv.reader(file)
    #     next(csv_reader)
    #     total = 0
    #     count = 0
    #     for row in csv_reader:
    #         total += float(row[1])
    #         count += 1
    #     average = total / count
    #     print(f"The average expense is: {average}")
    # return 0

def get_by_category():
    id = get_input_id()
    download_file(id)

    category_to_check = input("Enter the category: ")

    with open(f"expenses-E{id}.csv", mode='r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)
        categorie_sum = 0
        for row in csv_reader:
            amount = float(row[1])
            category = row[2]
            if category == category_to_check:
                categorie_sum += amount
        print(f"The total expense for category {category_to_check} is: {categorie_sum}")
    return 0

if __name__ == "__main__":
    copy_rexx_file()
    menu()
