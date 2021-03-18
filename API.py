from flask import Flask,request, render_template,redirect,url_for
from flask_restful import Api, Resource, reqparse
from flask import jsonify
from flask_cors import CORS
import pymysql
import mysql.connector
import os
from datetime import date
from datetime import datetime
import requests
import shutil
import subprocess
import mysql.connector
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
from json import dumps
import json


app = Flask(__name__)
api = Api(app)
CORS(app)
UPLOAD_FOLDER=os.getcwd()+"/download"
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

    def worker(self,file,id):
        BASE="http://127.0.0.1:5000/"
        print(file)
        current_dir=os.getcwd()
        file_from=os.getcwd()+"\\data\\"+file
        file_to=os.getcwd()+"\\download\\"
        file_run=os.getcwd()+"\\download\\"+file
        print(file_run)

        shutil.copy(file_from, file_to)
        print("Downloading File")
        os.system("cd download &&  echo 'Downloading tar file' && driver.sh && echo 'Extracting tar file' &&  echo 'Moving Content to system file' && @type %s > hello-handout/hello.c && driver.sh" %file)
        import subprocess
        output = os.system("echo 'Executing the job' && cd download/hello-handout && driver.sh ../%s && echo 'Score saved in output file'" %file)

        with open('download/hello-handout/output.txt','r') as file2:
            countriesStr = file2.read()

        countriesStr=countriesStr.strip('\n')

        response =requests.put(BASE + "getscores/%s" %id,{'score':str(countriesStr)})
        
        return (response.json())




    def get(self, id):
        conn = pymysql.connect(host="localhost", user="root", password="", db="autolab_development")
        myCursor = conn.cursor()
        

        myCursor.execute("""select filename from submissions where id=%s;""", id)
        data = myCursor.fetchall()

        for row in data:
            ext=(row[0].split(".")[1])
            # sqlFilename=row['filename']
            # sqlFilename.split(".")
            # print(sqlFilename)
            
        file = "submission-" + str(id) +"."+ str(ext)
        print(file)
        conn.commit()
        conn.close()
        file_to_move = os.getcwd() + "\\data\\" + file
        response=self.worker(file,id)

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




@app.route('/user_login', methods = ['POST'])
def user_login():
    conn=pymysql.connect(host="localhost",user="root",password="",db="autolab_development")
    email=(request.form['email'])
    password=request.form['password']
    query="select * from users WHERE email={email} and users.encrypted_password=PASSWORD({password})"
    if (len(query)==1):
        return "User existed"
    else:
        return "your email or password is incorrect"




#to make an assignment
@app.route('/assessments_register', methods = ['POST'])
def assessments_register():
  #storing tar
    file = request.files['tar'] 
    if not os.path.isdir(UPLOAD_FOLDER):
        os.mkdir(UPLOAD_FOLDER)
    filename=secure_filename(file.filename)
    destination="/".join([UPLOAD_FOLDER, filename])
    file.save(destination)
#storing make
    file2 = request.files['make']
    filename2=secure_filename(file2.filename)
    destination="/".join([UPLOAD_FOLDER, filename2])
    file2.save(destination)
    x=(request.form['name'])
    course=(request.form['course'])
    deadline=(request.form['deadline'])
    print(deadline)
    conn=pymysql.connect(host="localhost",user="root",password="",db="autolab_development")
    myCursor=conn.cursor()
    

    myCursor.execute("""insert into assessments (name,course_id,grading_deadline) values ('%s','%s','%s')"""%(x,1,deadline))
    assessments_id=myCursor.lastrowid
    myCursor.execute("""insert into attachments (filename,mime_type,course_id,assessment_id) values ('%s','%s','%s','%s')"""%(filename,'tar',1,assessments_id))
    print(assessments_id)
    conn.commit()
    return {"data":"done"}



#to submit a solution
@app.route('/submitSolution', methods = ['POST'])

def submitSolution():
    file = request.files['solution']
    filename2=file.filename 
    ext=filename2.split(".")[1]
    assessment_id= request.form['assessment_id']
    conn=pymysql.connect(host="localhost",user="root",password="",db="autolab_development")
    myCursor=conn.cursor()
    query="""INSERT INTO `submissions` ( course_user_datum_id, assessment_id, filename,  submitted_by_id) VALUES ('{}','{}','{}','{}')""".format(1,assessment_id,str(filename2),1)
    myCursor.execute(query)
    sub_id=myCursor.lastrowid
    print("submission-{}".format(sub_id))
    conn.commit()
    # #myCursor.execute("""insert into attachments (filename,mime_type,course_id,assessment_id) values ('%s','%s','%s','%s')"""%(filename,'tar',1,assessments_id))
    # print(assessments_id)
    destination="/".join([SOLUTION_FOLDER, "submission-{}.{}".format(str(sub_id),ext)])
    file.save(destination)
    return {"data":ext}


if __name__ == "__main__":
    app.run()
