from flask import Blueprint,current_app,make_response
from flask_wtf import csrf

html = Blueprint('web_html',__name__)

@html.route("/<re(r'.*'):html_file_name>") # 常用的数据类型：int float str(不能匹配/) path
def get_html(html_file_name):
    """提供静态html文件"""
    # 如果html_file_name为"",表示访问的路径时/,请求的是主页
    if not html_file_name:
        html_file_name = "index.html"
    # 如果浏览器不是favicon.icon
    if html_file_name != 'favicon.icon':
        html_file_name = "html/" + html_file_name
    # 创建一个csrf_token的值
    csrf_token = csrf.generate_csrf()

    # flask提供的访问静态文件的方法
    resp = make_response(current_app.send_static_file(html_file_name))
    # 设置cookie的值
    resp.set_cookie("csrf_token",csrf_token)
    return resp