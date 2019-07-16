from flask import Flask, render_template, request
from werkzeug import secure_filename
import requests
import os
import logging

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
        return render_template('index.html', ip=pub_ip)  
    except:
        logger.exception("Not able to get EC2 metadata. Not running on AWS?")
        return 'Something went wrong'

@app.route('/upload', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
        f = request.files['file']
        create_new_folder(UPLOAD_FOLDER)
        try:
            f.save(os.path.join(UPLOAD_FOLDER, secure_filename(f.filename))) # filename can then safely be stored on a regular file system
            result='File uploaded successfully'
        except:
            result='Failed to upload file'
            logger.exception(result)
        return result
                
if __name__ == '__main__':
   app.run(debug = True, host='0.0.0.0', port='80')