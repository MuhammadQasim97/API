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
    data = response.json()
    print(data)
    current_dir = os.getcwd()
    file_from = os.getcwd() + "\\data\\" + data['data']
    file_to = os.getcwd() + "\\download\\"
    file_run = os.getcwd() + "\\download\\" + data['data']

    shutil.copy(file_from, file_to)
    print("Downloading File")
    # os.system("gcc "+file_run)
    os.system(
        "cd download &&  echo 'Downloading tar file' && driver.sh && echo 'Extracting tar file' &&  echo 'Moving Content to system file' && @type %s > hello-handout/hello.c && driver.sh" %
        data['data'])
    import subprocess
    output = os.system(
        "echo 'Executing the job' && cd download/hello-handout && driver.sh ../%s && echo 'Score saved in output file'" %
        data['data'])

    with open('download/hello-handout/output.txt', 'r') as file:
        countriesStr = file.read()

    countriesStr = countriesStr.strip('\n')

    response = requests.put(BASE + "getscores/%s" % id, {'score': str(countriesStr)})
    print(response.json())


print("Choose one option")
print("1 is to get all submissions")
print("2 is to get make/tar files")
print("3 is to mark a submission")
opt = input()
if opt == '1':
    getAllSubmissions()
elif opt == '2':
    getMimeFiles()
elif opt=='3':
    markSubmission()
