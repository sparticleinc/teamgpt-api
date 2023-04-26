# 服务开发指南

## 一、框架说明

### 1.1 Python>=3.10

### 1.2 [FastAPI](https://fastapi.tiangolo.com/zh/) WEB框架

### 1.3 [Tortoise-ORM](https://tortoise.github.io/contrib/fastapi.html)  数据库ORM【使用PostgreSQL数据库】

### 1.4 uvicorn 服务运行库

## 二、快速开始

- 安装Python 3.10
- 拉取代码
- 设置python虚拟环境
    - `pip install virtualenv`
    - `virtualenv venv`
- 安装依赖 `pip install -r requirements.txt`
- 安装vscode，并安装扩展pylance
- 在项目根目录下创建.env，对应setting.py里面的配置
- 运行代码：`uvicorn circleo.app:app --reload` 或者  `python main.py`
- 安装pre-commit，执行：`pip install pre-commit`以及`pre-commit install`用于提交代码前格式检查

## 三、代码提交规范

- 新功能开发、较大改动的bug以及代码重构需要通过开分支提交，并请求其他成员进行代码review以及合并。通过github pull request
  提交合并请求。
- 分支说明
    - main分支为开发环境分支，最新代码在main分支体现
    - 合并到main分支前需要先解决代码冲突，由请求合并方负责冲突解决
    - 预发布版本将代码从main分支合并到pre分支
    - 正式版本将代码从main分支开出最新的wk分支（如果一周多个发布，则为合并）

## 四、运维说明

### 4.1 环境说明

- 开发环境 https://api.circleo.win
    - 配置文件：https://github.com/bieshu-Inc/coss-cluster-config/blob/main/circleo-dev/circleo-backend/config.yaml
    - 对应自动部署代码分支：main
- 预发布环境 https://api.circleo.pre
    - 配置文件：https://github.com/bieshu-Inc/coss-cluster-config/blob/main/circleo-pre/circleo-backend/config.yaml
    - 对应自动部署代码分支：pre
- 正式环境 https://api.circleo.me
    - 配置文件：https://github.com/bieshu-Inc/coss-cluster-config/blob/main/circleo/circleo-backend/config.yaml
    - 对应自动部署代码分支：wk分支，例如：2022.wk50

### 4.2 服务部署

### 4.3 运行日志

> 通过elastic查看

## 五、ORM生成初始化脚本

- Init ORM: `aerich init -t teamgpt.settings.TORTOISE_ORM` (Only fisrt, no need)
- Init database: `aerich init-db` (Only fisrt, no need)
- Make migrations: `aerich migrate`
- Migrate(to DB): `aerich upgrade`
- 注意：如果是同一功能的提交，尽量只使用一个sql脚本
- 小技巧：如果已经使用`aerich migrate`并进行了`aerich upgrade`。可以使用`aerich downgrade`
  回退版本，然后再进行`aerich migrate`以及`aerich upgrade`

## 六、国际化

### 6.1 翻译使用规范

## 七、EMQ事件通知

## 八、程序结构说明

## 九、HTTP 返回码

- 200 OK 接口请求正常
- 204 No Content 接口请求正常，但是服务器没有返回数据
- 400 Bad Request 客户端请求参数错误，例如，指定数字类型但是传入的是字符串
- 401 Unauthorized 没有登录授权
- 403 Forbidden 没有权限
- 404 Not Found 资源或接口不存在
- 405 Method Not Allowed 请求方式错误
- 422 Unprocessable Entity 请求参数格式错误
- 500 Internal Server Error 服务器错误，未处理异常