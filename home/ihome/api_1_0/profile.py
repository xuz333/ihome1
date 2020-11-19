from . import api
from ihome.utils.commons import login_required
from flask import g,jsonify,request,session,current_app
from ihome.utils.response_code import RET
from ihome.utils.image_storage import storage
from ihome.models import User
from ihome import db,constants


# 上传图片
@api.route('/users/avatar',methods=['POST'])
@login_required
def set_user_avatar():
    user_id = g.user_id
    image_file = request.files.get('avatar') # 获取图片
    if image_file is None:
        return jsonify(errno=RET.PARAMERR,errmsg='未上传图片')

    image_data = image_file.read()
    try:
        file_name = storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR,errmsg='上传图片失败')

    try:
        User.query.filter_by(id=user_id).update({'avatar_url':file_name})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='图片信息失败')
    avatar_url = constants.QINIU_URL_DOMAIN + file_name

    return jsonify(errno=RET.OK,errmsg='保存成功',data={'avatar_url':avatar_url})


# 修改用户名
@api.route('/users/name',methods=['PUT'])
@login_required
def change_user_name():
    user_id = g.user_id
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='获取用户信息失败')

    if user is None:
        return jsonify(errno=RET.NODATA,errmsg='无效操作')

    return jsonify(errno=RET.OK,errmsg='OK',data=user.to_dict())

# 获取用户实名认证信息
@api.route('/users/auth',methods=['GET'])
@login_required
def get_user_auth():
    user_id = g.user_id
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='获取实名认证信息失败')

    if user is None:
        return jsonify(errno=RET.NODATA,errmsg='无效操作')

    return jsonify(errno=RET.OK,errmsg='OK',data=user.auth_to_dict())


# 保存信息
@api.route("/users/auth",methods=["POST"])
@login_required
def set_user_auth():
    user_id = g.user_id
    # 获取参数
    req_data = request.get_json()
    if not req_data:
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误")

    real_name = req_data.get("real_name")# 获取真实姓名
    id_card = req_data.get("id_card") # 身份证号码
    # 参数校验
    if not all([real_name,id_card]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误")

    # 保存用户的姓名和身份证号码
    try:
        User.query.filter_by(id=user_id,real_name=None,id_card=None).update({"real_name":real_name,"id_card":id_card})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg="保存用户实名认证信息失败")

    return jsonify(errno=RET.OK,errmsg="OK")


