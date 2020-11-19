from flask import session
from flask_wtf import csrf
from ihome import create_app,db
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
# 创建flask的应用对象

#注意：在测试模式下日志处理会自动忽略掉我们的日志等级处理，只有在开发模式下才会正常
app = create_app("develop")
# app = create_app("product")
manager = Manager(app)

Migrate(app,db)
manager.add_command("db",MigrateCommand)

if __name__ == "__main__":
    manager.run()

