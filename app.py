from flask import Flask, render_template, request
from werkzeug import secure_filename
import requests
import os
pub_ip = requests.get("http://169.254.169.254/latest/meta-data/public-ipv4").content
app = Flask(__name__)
PROJECT_HOME = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = '{}/uploads'.format(PROJECT_HOME)
def create_new_folder(local_dir):
    newpath = local_dir
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    return newpath
@app.route('/upload')
def html():
   return render_template('upload.html', ip=pub_ip)     
@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      f = request.files['file']
      create_new_folder(UPLOAD_FOLDER)
      f.save(os.path.join(UPLOAD_FOLDER, secure_filename(f.filename))) # filename can then safely be stored on a regular file system
      return 'file uploaded successfully'
                
if __name__ == '__main__':
   app.run(debug = True)