import subprocess
import os
import csv
import random
from datetime import datetime

formatted_date = ""

def menu():
    while True:
        print("\nWhat do you want to do?")
        print("1. Enter expense")
        print("2. List files")
        print("3. Get expense data")
        print("4. Exit")

        choice = input("Enter your choice (1-3): ")

        if choice == '1':
            input_expenses()
        elif choice == '2':
            get_files()
        elif choice == '3':
            print("Exiting the menu. Goodbye!")
            break
        else:
            print("Invalid choice, please try again.")

def input_expenses():
    csv_file = 'expenses.csv'

    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
       
        writer.writerow(["Date", "Amount", "Category"])

        while True:
            date = input("Enter the date (YYYY-MM-DD): ")
            date_object = datetime.strptime(date, "%Y-%m-%d")
            global formatted_date 
            formatted_date = date_object.strftime("%y%m%d")
            amount = float(input("Enter the amount: "))
            category = input("Enter the expense category: ")

            # Write the current expense entry to the CSV file
            writer.writerow([date, amount, category])

            more = input("Would you like to add another expense? (y/n): ")
            if more.lower() != 'y':
                break


def upload_expenses_to_ds():
    list_command = f"zowe zos-files list ds Z58582.EXPENSES.E{formatted_date} -a"
    create_command = f"zowe zos-files create ds Z58582.EXPENSES.E{formatted_date}"
    delete_command = f"zowe zos-files delete ds Z58582.EXPENSES.E{formatted_date} -f"
    upload_command = f"zowe zos-files upload file-to-data-set \"expenses.csv\" \"Z58582.EXPENSES.E{formatted_date}\""

    list_ds = subprocess.run(list_command, shell=True, capture_output=True)
    str_stdout = list_ds.stdout.decode('utf-8')
    print(str_stdout)
    
    if (f"Z58582.EXPENSES.E{formatted_date}" is str_stdout):
        # TODO: possibility to merge entries with existing file when file exists, first download the file, get the entries, append to that file and upload again
        return 0
        # delete_ds = subprocess.run(delete_command, shell=True, capture_output=True)
        # print(delete_ds.stdout.decode('utf-8'))
        # print(delete_ds.stderr.decode('utf-8'))

    create_ds = subprocess.run(create_command, shell=True, capture_output=True)
    print(create_ds.stdout.decode('utf-8'))
    upload_ds = subprocess.run(upload_command, shell=True, capture_output=True)
    print(upload_ds.stdout.decode('utf-8'))

def get_files():
    # TODO: list all or specific file
    # TODO: download the file, convert to csv
    id = input("Enter the id of the expenses file (EXPENSES.E<ID>): ")
    list_command = f"zowe zos-files list ds Z58582.EXPENSES.E{id} -a"
    list_of_ds = subprocess.run(list_command, shell=True, capture_output=True).stdout.decode('utf-8')
    print(list_of_ds)

def merge_files():
    # TODO: from input entry, get all the files, turn into one and convert to csv
    return 0

def get_total():
    # TODO: run a calculation to get total amount spend 
    return 0

if __name__ == "__main__":
    menu()
