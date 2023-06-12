import datetime
import argparse
import uuid
import logging as rel_log
from datetime import timedelta
from flask import *
from processor.AIDetector_pytorch import Detector
from utils.logger import logger
from utils.logger import init as loggerInit

import core.main

UPLOAD_FOLDER = r'./uploads'

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'bmp'])
app = Flask(__name__)
app.secret_key = 'secret!'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

werkzeug_logger = rel_log.getLogger('werkzeug')
werkzeug_logger.setLevel(rel_log.ERROR)

loggerInit()

# 解决缓存刷新问题
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)


# 添加header解决跨域
@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-Requested-With'
    return response


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/')
def hello_world():
    return redirect(url_for('static', filename='./index.html'))


@app.route('/detect', methods=['GET', 'POST'])
def detect():
    file = request.files['file']
    if file and allowed_file(file.filename):
        fileBuffer = file.read()
        image_info = core.main.c_main(fileBuffer, current_app.model)
        if current_app.save == '1' or (current_app.log == '1' and len(image_info) > 0):
            save_picture(fileBuffer)
        logger.info("{0}:{1}".format(request.remote_addr,image_info))
        return jsonify({'status': 1, 'image_info': image_info})

    return jsonify({'status': 0})

def save_picture(fileBuffer):
    fileNmae = str(uuid.uuid1())
    with open("./picture/"+ fileNmae + ".png", 'wb+') as fs:
        fs.write(fileBuffer)
    logger.info("{0} saved".format(fileNmae))

def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', default=5003, help='port')
    parser.add_argument('--device', default='cpu', help='device')
    parser.add_argument('--save', default='0', help='save')
    parser.add_argument('--log', default='0', help='log')
    parser.add_argument('--model', default='final', help='final')
    parser.add_argument('--thres', default=0.25, help='conf_thres', type=float)
    opt = parser.parse_args()
    return opt


if __name__ == '__main__':
    opt = parse_opt()
    # opt.model = 'final_2_0'
    with app.app_context():
        current_app.model = Detector(opt.device, opt.model, opt.thres)
        current_app.save = opt.save
        current_app.log = opt.log
    app.run(host='0.0.0.0', port=opt.port)
