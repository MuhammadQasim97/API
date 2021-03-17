import pymysql
id=input("Enter the id:")
conn=pymysql.connect(host="localhost", user="root", port=8080, password="", db="autolab_development")
myCursor=conn.cursor()

myCursor.execute("""select assessment_id from submissions where id=%s;""",id)
assessment_id=myCursor.fetchall()

for row in assessment_id:
	print(row)

conn.commit()
conn.close()
