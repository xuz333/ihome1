from . import api
from flask import render_template,request,json,redirect,jsonify,current_app,session
from ihome.utils.response_code import RET
from ihome.models import User
from sqlalchemy.exc import IntegrityError
import re
from ihome import redis_storage,db,constants

@api.route('/users',methods=['POST'])
def register():
    red_dict = request.get_json()

    mobile = red_dict.get('mobile')
    sms_code = red_dict.get('sms_code')
    password = red_dict.get('password')
    password2 = red_dict.get('password2')

    if not all([mobile,sms_code,password,password2]):
        return jsonify(errno=RET.PARAMERR,errmsg='参数不完整')

    if not re.match(r"1[34578]\d{9}",mobile):
        return jsonify(errno=RET.PARAMERR,errmsg='手机号格式错误')

    if password != password2:
        return jsonify(errno=RET.PARAMERR,errmsg='密码不一致')

        # 从redis中取出短信验证码
    try:
        real_sms_code = str(redis_storage.get("sms_code_%s" % mobile), encoding="utf-8")
        print("real_sms_code=", real_sms_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="读取真实短信验证码异常")

        # 判断短信验证码是否过期
    if real_sms_code is None:
        return jsonify(errno=RET.NODATA, errmsg="短信验证码失效")

        # 删除redis中的短信验证码，防止重复使用校验
    try:
        redis_storage.delete("sms_code_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)

        # 判断用户填写的短信验证码的正确性
    if real_sms_code != sms_code:
        return jsonify(errno=RET.DATAERR, errmsg="短信验证码错误")

    user = User(name=mobile,mobile=mobile)
    user.password=password
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        # 数据库操作错误后的回滚
        db.session.rollback()
        # 表示手机号码出现了重复值，即手机号码已经注册过
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAEXIST, errmsg="手机号已经存在!")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据库异常")

    # 保存登录状态到session中
    session["name"] = mobile
    session["mobile"] = mobile
    session["user_id"] = user.id
    # 返回结果
    return jsonify(errno=RET.OK,errmsg="注册成功")

@api.route('/sessions',methods=['POST'])
def login():
    red_dict = request.get_json()
    # red_dict = request.get_data(parse_form_data=False)
    # red_dict = json.loads(red_dict,encoding='utf-8')
    mobile = red_dict.get('mobile')
    password = red_dict.get('password')
    # mobile = request.form.get('mobile')
    # password = request.form.get('password')
    print(mobile,password)

    if not all([mobile,password]):
        return jsonify(errno=RET.PARAMERR,errmsg='参数不完整')
    if not re.match(r'1[34578]\d{9}',mobile):
        return jsonify(errno=RET.PARAMERR,errmsg='手机号格式错误')
    user_ip = request.remote_addr
    try:
        access_nums= redis_storage.get('access_num_%s'%user_ip)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if access_nums is not None and int(access_nums)>=constants.LOGIN_ERROR_FORBID_TIME:
            return jsonify(errno=RET.REQERR,errmsg='错误次数过多')

    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取用户信息失败")

    if user is None or not user.check_passwd(password):
        try:
            redis_storage.incr("access_num_%s"%user_ip)  # 加一
            redis_storage.expire("access_num_%s"%user_ip,constants.LOGIN_ERROR_FORBID_TIME)
        except Exception as e:
            current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="用户名或者密码错误")
    session["name"] = user.name
    session["mobile"] = user.mobile
    session["user_id"] = user.id
    return jsonify(errno=RET.OK, errmsg="登录成功")

@api.route('/session',methods=['GET'])
def check_login():
    name = session.get('name')
    if name is not None:
        return jsonify(errno=RET.OK,errmsg='true',data={'name':name})
    else:
        return jsonify(errno=RET.SESSIONERR,errmsg='false')


@api.route('/session',methods=['DELETE'])
def logout():
    csrf_token = session.get('csrf_token')
    session.clear()
    session['csrf_token']=csrf_token
    return jsonify(errno=RET.OK,errmsg='OK')





