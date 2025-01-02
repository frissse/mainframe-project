PREREQUISITES

- make sure zowe clie tool is installed & configured to be used with your zOS main frame account

if that is not the case, follow the instructions on this link: https://docs.zowe.org/stable/getting-started/overview

- make sure you have python installed, install the dependencies in the requirements.txt file

```
pip3 install -r requirements.txt 
```

next is navigating to the folder where the main.py file is situated and running it

```
python3 main.py
```

follow the CLI menu to start the zMoneyTracker

some notes & clarifications

- the ID of the file is always YYYYMM
- the tool stores your zID in a file, so it does not need to ask you every single time you run the program
- when (first) starting the tool, it seems slow, this is because it checks if the REXX scripts are stored on your mainframe account or not, if not it transfer the AVGREXX & SUMREXX file to the correct location to run
