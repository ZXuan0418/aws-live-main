from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('UpdateEmp.html')


@app.route("/about", methods=['POST'])
def about():
    return render_template('www.intellipaat.com')


@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=emp_name)

#get employee codes
@app.route("/getemp", methods=['GET','POST'])
def GetEmp():
    return render_template('GetEmp.html')

@app.route("/fetchdata", methods=['POST'])
def GetEmpOutput():
    emp_id = request.form['emp_id']
    select_sql = "SELECT * FROM employee WHERE emp_id = %s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql, (emp_id))
        db_conn.commit()
        
        (emp_id, first_name, last_name, pri_skill, location) = cursor.fetchone()
        
        # emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        # s3 = boto3.resource('s3')
        # s3.Bucket(custombucket).download_file(emp_image_file_name_in_s3, emp_image_file_name_in_s3)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('GetEmpOutput.html', id=emp_id, fname=first_name, lname=last_name, interest=pri_skill, location=location)

#update employee code
@app.route("/updateemp", methods=['GET', 'POST'])
def UpdateEmp():
    emp_id = request.form['emp_id']

    get_sql = "SELECT * FROM employee WHERE emp_id = %s"

    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file'] 

    update_sql = "UPDATE INTO employee SET first_name = %s, last_name = %s, pri_skill = %s, location = %s WHERE emp_id = %s"
    cursor = db_conn.cursor()
    
    try:
        cursor.execute(update_sql, (first_name, last_name, pri_skill, location, emp_id))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data updated in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("All modification done...")
    return render_template('UpdateEmp.html', name=emp_name)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
