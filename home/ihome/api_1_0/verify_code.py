from . import api
from ihome.utils.captcha.captcha import captcha
from ihome import redis_storage,constants,db
from flask import current_app,jsonify,make_response,request

from ihome.utils.response_code import RET
from ihome.models import User
import random
from ihome.libs.yuntongxun.sms import CCP
# from ihome.tasks.task_sms import send_sms
# from ihome.tasks.sms.tasks import send_sms
# from ihome.tasks.sms import tasks

# GET 127.0.0.1/api/v1.0/image_codes/<image_code_id>

@api.route("/image_codes/<image_code_id>")
def get_image_code(image_code_id):
    """
    获取图片验证码
    :param image_code_id: 图片验证码编号
    :return:正常：验证码图片,异常：返回json
    """
    # 业务逻辑处理
    # 生成验证码图片
    #图片验证码的名字，真实的文本内容，图片对应的二进制数据
    name,text,image_data = captcha.generate_captcha()
    # 将验证码真实值与编号保存到redis中，设置有效期
    # redis中的数据类型：字符串，列表，哈希,set
    # "key":xxx
    # "image_codes":["编号":"真实值","编号":"真实值"],不方便取数据
    # "image_codes":{"id1":"abc","id2":"def"},
    # 设置值：hset("image_codes","id1","abc"),hset("image_codes","id2","def")
    # 获取值：hget("image_codes","id1")==>abc
    # 但是对于设置有效期不方便，因为有效期是设置给单条记录的，这样所有数据组成一条记录，不方便设置有效期
    # 对于单条记录的维护，建议选择字符串
    # "image_code_编号1":"真实值"
    # "image_code_编号2":"真实值"
    # redis_storage.set("image_code_%s"%image_code_id,text)
    # # redis_storage.expire("image_code_%s"%image_code_id,180) # 有效期180秒，不建议写死，可以提供常量
    # redis_storage.expire("image_code_%s"%image_code_id,constants.IMAGE_CODE_REDIS_EXPIRES) # 有效期180秒，不建议写死，可以提供常量

    try:
        redis_storage.setex("image_code_%s"%image_code_id,constants.IMAGE_CODE_REDIS_EXPIRES,text)
    except Exception as e:
        # 记录日志
        current_app.logger.error(e)
        # return jsonify(errno=RET.DATAERR,errmsg="save image_code_id failed")
        return jsonify(errno=RET.DATAERR,errmsg="保存图片验证码失败")

    # 返回图片
    resp = make_response(image_data)
    resp.headers["Content-Type"] = "image/jpg"
    return resp


# # GET /api/v1.0/sms_codes/<mobile>?image_code=xxx&image_code_id=xxx
# @api.route("/sms_codes/<re(r'1[34578]\d{9}'):mobile>")
# def get_sms_code(mobile):
#     """获取短信验证码"""
#     # 获取参数
#     image_code = request.args.get("image_code")
#     image_code_id = request.args.get("image_code_id")
#     print("image_code=",image_code,"image_code_id=",image_code_id)
#     # 校验参数
#     if not all([image_code,image_code_id]):
#         # 表示参数不完整
#         return jsonify(errno=RET.PARAMERR,errmsg="参数不完整")
#     # 业务逻辑处理
#     # 从redis中取出真实的图片验证码
#     try:
#         real_image_code = str(redis_storage.get("image_code_%s"%image_code_id),encoding="utf-8")
#         print("real_image_code=",real_image_code)
#     except Exception as e:
#         current_app.logger.error(e)
#         return jsonify(errno=RET.DBERR,errmsg="redis数据库异常")
#
#     # 判断图片验证码是否过期
#     if real_image_code is None:
#         # 表示图片验证码没有或者过期
#         return jsonify(errno=RET.NODATA,errmsg="图片验证码失效")
#
#     #删除redis中图片验证码，防止用户使用同一个图片验证码验证多次
#     try:
#         redis_storage.delete("image_code_%s"%image_code_id)
#     except Exception as e:
#         current_app.logger.error(e)
#
#     # 与用户填写的值进行比较
#     if real_image_code.lower() != image_code.lower():
#         # 表示用户填写错误
#         return jsonify(errno=RET.DATAERR,errmsg="图片验证码错误")
#
#     # 判断对于这个手机号的操作，在60秒之内有没有之前的记录，如果有，认为用户操作频繁，不接受处理
#     try:
#         send_flag = redis_storage.get("send_sms_code_%s"%mobile)
#     except Exception as e:
#         current_app.logger.error(e)
#     else:
#         if send_flag is not None:
#             #表示60秒之前有过发送记录
#             return jsonify(errno=RET.REQERR,errmsg="请求过于频繁，请求60秒后重试！")
#
#     try:
#         # 判断手机号是否存在
#         user = User.query.filter_by(mobile=mobile).first()
#     except Exception as e:
#         current_app.logger.error(e)
#     else:
#         if user is not None:
#             # 表示手机号码已经存在
#             return jsonify(errno=RET.DATAEXIST,errmsg="手机号已经存在!")
#
#     # 如果手机号不存在，则生成短信验证码
#     sms_code = "%06d" % random.randint(0,999999)
#     print("sms_code=",sms_code)
#     # 保存真实的短信验证码
#     try:
#         redis_storage.setex("sms_code_%s" % mobile,constants.SMS_CODE_REDIS_EXPIRES,sms_code)
#         # 保存发送给这个手机号码的记录，防止用户60秒内再次发出发送验证码的请求
#         redis_storage.setex("send_sms_code_%s"%mobile,constants.SEND_SMS_CODE_INTERVAL,1)
#     except Exception as e:
#         current_app.logger.error(e)
#         return jsonify(errno=RET.DBERR,errmsg="保存短信验证码异常")
#     # 发送短信
#     try:
#         cpp = CCP()
#         result = cpp.send_Template_sms(mobile,[sms_code,int(constants.SMS_CODE_REDIS_EXPIRES/60)],1)
#         print("result=", result)
#     except Exception as e:
#         current_app.logger.error(e)
#         return jsonify(errno=RET.THIRDERR, errmsg="发送短信异常")
#
#     # 返回值
#     if result == True:
#         # 发送成功
#         return jsonify(errno=RET.OK,errmsg="发送成功")
#     else:
#         # 发送失败
#         return jsonify(errno=RET.THIRDERR,errmsg="发送失败")

# GET /api/v1.0/sms_codes/<mobile>?image_code=xxx&image_code_id=xxx

@api.route("/sms_codes/<re(r'1[34578]\d{9}'):mobile>")
def get_sms_code(mobile):
    """获取短信验证码"""
    # 获取参数
    image_code = request.args.get("image_code")
    image_code_id = request.args.get("image_code_id")
    print("image_code=",image_code,"image_code_id=",image_code_id)
    # 校验参数
    if not all([image_code,image_code_id]):
        # 表示参数不完整
        return jsonify(errno=RET.PARAMERR,errmsg="参数不完整")
    # 业务逻辑处理
    # 从redis中取出真实的图片验证码
    try:
        real_image_code = str(redis_storage.get("image_code_%s"%image_code_id),encoding="utf-8")
        print("real_image_code=",real_image_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="redis数据库异常")

    # 判断图片验证码是否过期
    if real_image_code is None:
        # 表示图片验证码没有或者过期
        return jsonify(errno=RET.NODATA,errmsg="图片验证码失效")

    #删除redis中图片验证码，防止用户使用同一个图片验证码验证多次
    try:
        redis_storage.delete("image_code_%s"%image_code_id)
    except Exception as e:
        current_app.logger.error(e)

    # 与用户填写的值进行比较
    if real_image_code.lower() != image_code.lower():
        # 表示用户填写错误
        return jsonify(errno=RET.DATAERR,errmsg="图片验证码错误")

    # 判断对于这个手机号的操作，在60秒之内有没有之前的记录，如果有，认为用户操作频繁，不接受处理
    try:
        send_flag = redis_storage.get("send_sms_code_%s"%mobile)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if send_flag is not None:
            #表示60秒之前有过发送记录
            return jsonify(errno=RET.REQERR,errmsg="请求过于频繁，请求60秒后重试！")

    try:
        # 判断手机号是否存在
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
    else:
        if user is not None:
            # 表示手机号码已经存在
            return jsonify(errno=RET.DATAEXIST,errmsg="手机号已经存在!")

    # 如果手机号不存在，则生成短信验证码
    sms_code = "%06d" % random.randint(0,999999)
    print("sms_code=",sms_code)
    # 保存真实的短信验证码
    try:
        redis_storage.setex("sms_code_%s" % mobile,constants.SMS_CODE_REDIS_EXPIRES,sms_code)
        # 保存发送给这个手机号码的记录，防止用户60秒内再次发出发送验证码的请求
        redis_storage.setex("send_sms_code_%s"%mobile,constants.SEND_SMS_CODE_INTERVAL,1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="保存短信验证码异常")

    # 发送短信
    # 使用celery异步发送短信，delay()函数调用后立即返回
    # send_sms.delay(mobile,[sms_code,int(constants.SMS_CODE_REDIS_EXPIRES/60)],1)
    # 返回的是异步执行结果对象
    # result = tasks.send_template_sms.delay(mobile,[sms_code,int(constants.SMS_CODE_REDIS_EXPIRES/60)],1)
    # print("result=",result,"result.id=",result.id)
    # # 通过get()方法能够捕获celery异步执行的结果
    # # get()方法默认是阻塞行为，会等到有了执行结果后才返回
    # #get()方法也接受参数timeout,表示超时时间，如果时间到了还没有得到返回结果在返回
    # ret = result.get(timeout=1)
    # print("ret=",ret)
    # 发送成功
    return jsonify(errno=RET.OK,errmsg="发送成功")


