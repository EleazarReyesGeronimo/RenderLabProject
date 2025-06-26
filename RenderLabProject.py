from flask import Flask, app, render_template, request, redirect, url_for
import os

app = Flask(__name__)

app.route('/index')
def index():
    return render_template(index.html)

@app.route('/upload', methods=['POST'])
def upload_file():

    os.system(f"lftp -c 'open -u RendAdmin,C6mEyc:qcy public-ipaddress; put -O / {temp_file_path}'")