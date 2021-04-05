import requests
import os
import shutil
import subprocess
import pymysql
from datetime import date
from datetime import datetime

def getAllSubmissions():
    id = input("Enter ID of the assessment")

    BASE = "http://127.0.0.1:5000/"

    response = requests.get(BASE + "helloworld/" + id)
    data = response.json()
    print(data)


def getMimeFiles():
    id = input("Enter your submission_id")

    BASE = "http://127.0.0.1:5000/"

    response = requests.get(BASE + "hit/" + id)
    data = response.json()
    print(data)
    file_type1 = ".tar"
    file_type2 = ".make"
    file_to_move = os.getcwd() + "\\Files\\" + data['data'] + file_type1
    file_to_move1 = os.getcwd() + "\\Files\\" + data['data'] + file_type2
    shutil.move(file_to_move, os.getcwd() + "\\download\\")
    shutil.move(file_to_move1, os.getcwd() + "\\download\\")
    print(os.getcwd())


def markSubmission():
    id = input("ENTER ID TO DOWNLOAD FILE")

    BASE = "http://127.0.0.1:5000/"

    response = requests.get(BASE + "getsubmission/" + id)
    req=response.json()
    data=req['data']
    test_case=data['test_case']
    #id2=data['id']
    file=data['file']
    current_dir=os.getcwd()
    file_test_case=os.getcwd()+"\\download\\test-cases\\"+test_case
    file_from=os.getcwd()+"\\data\\"+file
    file_to=os.getcwd()+"\\download\\"
    file_run=os.getcwd()+"\\download\\"+file
    print(file_run)

    shutil.copy(file_from, file_to)
    shutil.copy(file_test_case,file_to)
    print("Downloading File")
    os.system("cd download &&  echo 'Downloading tar file' && driver.sh && echo 'Extracting tar file' &&  echo 'Moving Content to system file' && @type %s > work-room/hello.c && @type %s > work-room/test_case.c && driver.sh" %(file,test_case))
    import subprocess
    output = os.system("echo 'Executing the job' && cd download/work-room && driver.sh ../%s && echo 'Score saved in output file'" %file)

    with open('download/work-room/output.txt','r') as file2:
        countriesStr = file2.read()

    countriesStr=countriesStr.strip('\n')

    response =requests.put(BASE + "getscores/%s" %id,{'score':str(countriesStr)})
    
    print (response.json())


print("Choose one option")
print("1 is Mark submissions")
opt = input()
if opt == '1':
    markSubmission()

    
