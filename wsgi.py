#!/usr/bin/env python3
import os
from app import create_app

# 设置生产环境
os.environ['FLASK_CONFIG'] = 'production'
os.environ['FLASK_DEBUG'] = '0'

# 加载生产环境变量
from dotenv import load_dotenv
load_dotenv('.env.production')

app = create_app()

if __name__ == '__main__':
    app.run()