from flask import Flask,request, render_template,redirect,url_for
from flask_restful import Api, Resource, reqparse
from flask import jsonify
from flask_cors import CORS
import pymysql
import mysql.connector
import os
import tkinter
from datetime import date
from tkinter import *
#from datetime import datetimef
import requests
import shutil
import subprocess
import mysql.connector
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
from json import dumps
import json
from tkinter import filedialog



app = Flask(__name__)
api = Api(app)
CORS(app)
UPLOAD_FOLDER=os.getcwd()+"/download/test-cases"
SOLUTION_FOLDER=os.getcwd()+"/data"
class getAssessments(Resource):
    def get(self, id):
        conn = pymysql.connect(host="localhost", user="root", password="", db="autolab_development",)
        myCursor = conn.cursor()

        myCursor.execute("""select id, name, grading_deadline from assessments where course_id=%s;""", id)
        print("""select id, name, due_at from assessments where course_id=%s;""", id)
        data = myCursor.fetchall()
        send=list()
        for x in data:
            x=list(x)
            x[2]=x[2].strftime("%d-%b-%Y (%H:%M:%S)")
            print(x[2])
            send.append(x)

        print(send)

        return {"data": send}

api.add_resource(getAssessments, "/getassessments/<int:id>")


class HIT(Resource):
    def get(self, id):

        conn = pymysql.connect(host="localhost", user="root", password="", db="autolab_development")
        myCursor = conn.cursor()

        myCursor.execute("""SELECT assessment_id FROM submissions WHERE id=%s;""", id)
        assessment_id = myCursor.fetchall()

        for x in assessment_id:
            print(x)

        file_type1 = ".tar"
        file_type2 = ".make"

        myCursor.execute("""select filename from attachments where assessment_id=%s && mime_type=%s;""",
                         (assessment_id, file_type1))
        i = ''.join(str(x) for x in myCursor.fetchall())
        print(i)

        j = str.strip(i).strip("/[{(',')}]/g")
#        k = str.strip(j).strip(",")
#        l = str.strip(k).strip("''")
        print(j)
        data = str(j)
#        data1 = str(j) + file_type2
#        print(data, data1)
        print(data)
        conn.commit()
        if conn:
            conn.close()

        return {"data": data}


api.add_resource(HIT, "/hit/<int:id>")

class HelloWorld(Resource):

	def get(self,id):

		conn = pymysql.connect(host="localhost", user="root", password="", db="autolab_development", port=8111, connect_timeout=1000)
		myCursor = conn.cursor()

		myCursor.execute("""SELECT id from submissions WHERE assessment_id=%s;""",id)
		SUB_IDS = myCursor.fetchall()
		for row in SUB_IDS:
			print(row)

		return {"data":SUB_IDS}

api.add_resource(HelloWorld,"/helloworld/<int:id>")


class getSubmission(Resource):

    def worker(self,file,id,test_case):
        BASE="http://127.0.0.1:5000/"
        print(file)
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
        
        return (response.json())




    def get(self, id):
        conn = pymysql.connect(host="localhost", user="root", password="", db="autolab_development")
        myCursor = conn.cursor()
        

        myCursor.execute("""select filename,assessment_id from submissions where id=%s;""", id)
        data = myCursor.fetchall()
        print(data)
        for row in data:
            ext=(row[0].split(".")[1])
            assessment_id=row[1]
            # sqlFilename=row['filename']
            # sqlFilename.split(".")
            # print(sqlFilename)
        myCursor.execute("""select filename from attachments where assessment_id=%s;""", assessment_id)
        data = myCursor.fetchall()

        for row in data:
            extTest=row[0].split(".")[1]
            
        file = "submission-" + str(id) +"."+ str(ext)
        test_case = "test-case-" + str(assessment_id) +"."+ str(extTest)
        print(file)
        conn.commit()
        conn.close()
        file_to_move = os.getcwd() + "\\data\\" + file
        print(test_case)
        #response=self.worker(file,id,test_case)
        response={"file":file,"id":"id","test_case":test_case}

        return {"data": response}

    def post(self, id):
        return {"data": id}


api.add_resource(getSubmission, "/getsubmission/<int:id>")

score_data = reqparse.RequestParser()
score_data.add_argument("score", type=str, help="Score not provided", required=True)


class getScores(Resource):
    def get(self, id):

        return {"data": "SCORES"}

    def put(self, id):
        scores = score_data.parse_args()
        score = scores['score']
        submission_id = id
        conn = pymysql.connect(host="localhost", user="root", password="", db="autolab_development")
        myCursor = conn.cursor()
        myCursor.execute("""select * from submissions where id=%s;""" % submission_id)

        if myCursor.rowcount <= 0:
            
            myCursor.execute("""update submissions set autoresult='%s' where id='%s';""" % (score,  submission_id))
            print("""update submissions set autoresult='%s' where id='%s';""" % (score,  submission_id))
        else:
            myCursor.execute("""update submissions set autoresult='%s' where id='%s';""" % (score,  submission_id))
            print("Score Updated")

        conn.commit()
        conn.close()
        return {"data": "Marked"}, 200


api.add_resource(getScores, "/getscores/<int:id>")





@app.route('/user_register', methods = ['POST'])



def user_register():
    conn=pymysql.connect(host="localhost",user="root",password="",db="autolab_development")
    firstName=(request.form['firstname'])
    lastName=request.form['lastname']
    email=request.form['email']
    password=request.form['password']
    response={
    'body':"",
    'code':404
    }
    response['body']="User addedd Successfull"
    response['code']=200
    admin=1 if request.form['type']=='teacher' else 0

    myCursor=conn.cursor()
    try:
        myCursor.execute("""insert into users (email,first_name,last_name,administrator,encrypted_password) values ('%s','%s','%s','%s',(SELECT PASSWORD('%s'))) ;""" % (email,firstName,lastName,admin,password))
    except(mysql.connector.Error) as e:
        response['code']=210
        response['body']=e
    conn.commit()
    conn.close()
    return{"data":response}
    
@app.route('/get_all_submissions', methods = ['GET'])
def get_all_submissions():
    conn=pymysql.connect(host="localhost",user="root",password="",db="autolab_development")
    myCursor=conn.cursor()
    myCursor.execute("""select * from submissions;""")
    records=myCursor.fetchall()
    return{"data":records}



@app.route('/get_courses', methods = ['GET'])
def get_courses():
    conn=pymysql.connect(host="localhost",user="root",password="",db="autolab_development")
    myCursor=conn.cursor()
    myCursor.execute("""select * from courses;""")
    records=myCursor.fetchall()
    return{"data":records}



@app.route('/user_login', methods = ['POST'])
def user_login():
    conn=pymysql.connect(host="localhost",user="root",password="",db="autolab_development")
    email=(request.form['email'])
    password=request.form['password']
    myCursor=conn.cursor()
    myCursor.execute("""select * from users WHERE email='%s' and users.encrypted_password=PASSWORD('%s');""" % (email,password))
    records=myCursor.fetchall()
    if (len(records)>=1):
        return {"data":records}
    else:
        return {"data":False}




#to make an assignment
@app.route('/assessments_register', methods = ['POST'])
def assessments_register():
  #storing tar
   
#storing make
    # file2 = request.files['make']
    # filename2=secure_filename(file2.filename)
    # destination="/".join([UPLOAD_FOLDER, filename2])
    # file2.save(destination)
    x=(request.form['name'])
    deadline=(request.form['deadline'])
    print(deadline)
    conn=pymysql.connect(host="localhost",user="root",password="",db="autolab_development")
    myCursor=conn.cursor()
    

    myCursor.execute("""insert into assessments (name,course_id,grading_deadline) values ('%s','%s','%s')"""%(x,1,deadline))
    assessments_id=myCursor.lastrowid
    file = request.files['test_case'] 
    if not os.path.isdir(UPLOAD_FOLDER):
        os.mkdir(UPLOAD_FOLDER)
    filename=secure_filename(file.filename)
    ext=filename.split(".")[1]
    destination="/".join([UPLOAD_FOLDER,  "test-case-{}.{}".format(str(assessments_id),ext)])
    file.save(destination)
    myCursor.execute("""insert into attachments (filename,mime_type,course_id,assessment_id) values ('%s','%s','%s','%s')"""%(filename,ext,1,assessments_id))
    print(assessments_id)
    conn.commit()
    return {"data":"done"}




@app.route('/add_course', methods = ['POST'])
def add_course():
  #storing tar
    courseName=(request.form['courseName'])
    #teacherid=(request.form['teacher'])
    teacherid=1
    startDate=(request.form['startDate'])
    endDate=(request.form['endDate'])
    semester=request.form['semester']
    conn=pymysql.connect(host="localhost",user="root",password="",db="autolab_development")
    myCursor=conn.cursor()
    

    myCursor.execute("""insert into courses (name,semester,start_date,end_date) values ('%s','%s','%s','%s')"""%(courseName,semester,startDate,endDate))
    course_id=myCursor.lastrowid
    myCursor.execute("""insert into  course_user_data (course_id,instructor,user_id) values ('%s','%s','%s')"""%(course_id,teacherid,teacherid))
    conn.commit()
    return {"data":"done"}

#to submit a solution
# @app.route('/submitSolution', methods = ['POST'])

# def submitSolution():
#     file = request.files['solution']
#     filename2=file.filename 
    # ext=filename2.split(".")[1]
    # assessment_id= request.form['assessment_id']
    # conn=pymysql.connect(host="localhost",user="root",password="",db="autolab_development")
    # myCursor=conn.cursor()
    # query="""INSERT INTO `submissions` ( course_user_datum_id, assessment_id, filename,  submitted_by_id) VALUES ('{}','{}','{}','{}')""".format(1,assessment_id,str(filename2),1)
    # myCursor.execute(query)
    # sub_id=myCursor.lastrowid
    # print("submission-{}".format(sub_id))
    # conn.commit()
    # # #myCursor.execute("""insert into attachments (filename,mime_type,course_id,assessment_id) values ('%s','%s','%s','%s')"""%(filename,'tar',1,assessments_id))
    # # print(assessments_id)
    # destination="/".join([SOLUTION_FOLDER, "submission-{}.{}".format(str(sub_id),ext)])
    # file.save(destination)
    # return {"data":ext}



#to submit a solution
@app.route('/submitSolution', methods = ['POST'])

def submitSolution():
    student_name=input("Enter Your Name")
    print("Now select the solution File")
    file_name=filedialog.askopenfilename(initialdir='/documents',title='Select A File',filetypes=(("cpp files","*.cpp"),("all types","*.*")))
    # file = request.files['solution']
    # filename2=file.filename 
    # ext=filename2.split(".")[1]
    # assessment_id= request.form['assessment_id']
    conn=pymysql.connect(host="localhost",user="root",password="",db="autolab_development")
    myCursor=conn.cursor()
    query="""INSERT INTO `submissions` (student_name, filename) VALUES ('{}','{}')""".format(str(student_name),str(file_name))
    myCursor.execute(query)
    
    # sub_id=myCursor.lastrowid
    # print("submission-{}".format(sub_id))
    conn.commit()
    print("Upload Successful")
    # # #myCursor.execute("""insert into attachments (filename,mime_type,course_id,assessment_id) values ('%s','%s','%s','%s')"""%(filename,'tar',1,assessments_id))
    # # print(assessments_id)
    # destination="/".join([SOLUTION_FOLDER, "submission-{}.{}".format(str(sub_id),ext)])
    # file.save(destination)
    # return {"data":ext}


submitSolution()
if __name__ == "__main__":
    app.run()
