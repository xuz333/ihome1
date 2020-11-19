# coding=utf-8

from ihome.libs.yuntongxun.CCPRestSDK import REST

# import ConfigParser

# 主帐号
accountSid = '8aaf07086e0115bb016e873e16fe4da6'

# 主帐号Token
accountToken = '0f59d259bae548a390fe1607d38a6f23'

# 应用Id
appId = '8aaf07086e0115bb016e873e175a4dad'

# 请求地址，格式如下，不需要写http://
serverIP = 'app.cloopen.com'

# 请求端口
serverPort = '8883'

# REST版本号
softVersion = '2013-12-26'


# 发送模板短信
# @param to 手机号码
# @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
# @param $tempId 模板Id


class CCP(object):
    '''自己封装的发送短信的辅助类'''
    # 用来保存对象的类属性
    instance = None

    def __new__(cls):
        # 判断CCP类有没有已经创建好的对象
        if cls.instance is None:
            obj = super(CCP, cls).__new__(cls)

            # 初始化REST SDK
            obj.rest = REST(serverIP, serverPort, softVersion)
            obj.rest.setAccount(accountSid, accountToken)
            obj.rest.setAppId(appId)

            cls.instance = obj

        return cls.instance

    def send_Template_sms(self, to, datas, temp_Id):
        # 初始化REST SDK

        result = self.rest.sendTemplateSMS(to, datas, temp_Id)
        for k, v in result.items():

            if k == 'templateSMS':
                for k, s in v.items():
                    print('%s:%s' % (k, s))
            else:
                print('%s:%s' % (k, v))

                # sendTemplateSMS(手机号码,内容数据,模板Id)


if __name__ == "__main__":
    ccp = CCP()
    # 1代表模板ID，下载SDK的官网api文档有说明
	# 这里填测试号码 免费发送短信  填的不是测试号码收短信费用
    # ret = ccp.send_Template_sms("填测试号码", ["短信内容", "有效时间"], 1)
    ret = ccp.send_Template_sms("15033889441", ["4753", "5"], 1)
    # 收到的短信内容为：【云通讯】您使用的是云通讯短信模板，您的验证码是4753，请于5分钟内正确输入

    print(ret)