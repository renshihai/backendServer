#!/usr/bin/env python3
import os
from app import create_app

# 设置开发环境
# os.environ['FLASK_CONFIG'] = 'development'
# os.environ['FLASK_DEBUG'] = '1'
config_name = os.environ.get('FLASK_CONFIG', 'development')
debug = os.environ.get('FLASK_DEBUG', '1') == '1'

# if False:
#     # 设置生产环境
#     os.environ['FLASK_CONFIG'] = 'production'
#     os.environ['FLASK_DEBUG'] = '0'
#     # 设置环境变量默认值，Railway 的环境变量会覆盖这些
#     # os.environ.setdefault('FLASK_CONFIG', 'production')
#     # os.environ.setdefault('FLASK_DEBUG', '0')

app = create_app(config_name)

if __name__ == '__main__':
    # 开发环境运行
    port = int(os.environ.get('PORT', 7000))

    app.run(
        # host=app.config['HOST'],
        # port=app.config['PORT'],
        # debug=app.config['DEBUG']
        host=app.config.get('HOST', '0.0.0.0'),
        port=port,
        debug=debug
    )