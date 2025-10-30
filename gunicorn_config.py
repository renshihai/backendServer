# Gunicorn 配置文件
import multiprocessing

# 服务器绑定
bind = "0.0.0.0:7000"

# 工作进程数
workers = multiprocessing.cpu_count() * 2 + 1

# 工作模式
worker_class = "sync"

# 最大请求数
max_requests = 1000
max_requests_jitter = 100

# 超时设置
timeout = 30

# 日志配置
accesslog = "-"
errorlog = "-"
loglevel = "info"

# 进程名称
proc_name = "tracking_app"

# 预加载应用
preload_app = True