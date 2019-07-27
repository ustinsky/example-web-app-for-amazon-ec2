from flask import Flask, render_template, request, redirect
from werkzeug import secure_filename
import requests
import os
import logging
import peewee
from peewee import *
import cryptography
import boto3

s3client = boto3.client('s3')
ssmclient = boto3.client('ssm', region_name='eu-central-1')

params = {'DB_USER': '', 'DB_PASS': '', 'DB_URL': '', 'S3_FILE_BUCKET': ''}

for key in params:
    response = ssmclient.get_parameter(
        Name=key,
        WithDecryption=True|False
    )
    params[key]=response['Parameter']['Value']

db = MySQLDatabase('dev', user=params['DB_USER'], passwd=params['DB_PASS'], host=params['DB_URL'])

class File(peewee.Model):
    result = peewee.TextField()
    filename = peewee.TextField()

    class Meta:
        database = db

db.connect()
db.create_tables([File])

logger = logging.getLogger()
logger.setLevel(logging.INFO)
app = Flask(__name__)
PROJECT_HOME = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = '{}/uploads'.format(PROJECT_HOME)

def create_new_folder(local_dir):
    newpath = local_dir
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    return newpath

@app.route('/')
def html():
    try:
        pub_ip = requests.get("http://169.254.169.254/latest/meta-data/public-ipv4", timeout=10).content
        #pub_ip = 'localhost' # uncomment for local testing
        all_results = []
        for r in File.select():
            all_results.append([r.result, r.filename])
        return render_template('index.html', ip=pub_ip.decode('utf-8'), results=all_results)  
    except:
        logger.exception("Not able to get EC2 metadata. Not running on AWS?")
        return 'Something went wrong'

@app.route('/upload', methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        create_new_folder(UPLOAD_FOLDER)
        try:
            s3client.upload_fileobj(f, Bucket=params['S3_FILE_BUCKET'], Key=f.filename)
            result='File uploaded successfully'
        except:
            result='Failed to upload file'
            logger.exception(result)
        file = File(result=result, filename=f.filename)
        file.save()
        return result
    else:
        return redirect('/')
                
if __name__ == '__main__':
   app.run(debug = True, host='0.0.0.0', port='80')
