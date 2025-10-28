#!/usr/bin/env python3
import os
from app import create_app

# 设置开发环境
os.environ['FLASK_CONFIG'] = 'development'
os.environ['FLASK_DEBUG'] = '1'

app = create_app()

if __name__ == '__main__':
    # 开发环境运行
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )