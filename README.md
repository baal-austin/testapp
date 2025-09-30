# 英语学习图谱API

基于FastAPI和SQLModel的英语学习图谱后端API。

## 功能特性

- 单词管理
- 关系图谱
- 用户系统
- 贡献审核
## 环境
- 使用uv
- 运行环境：Python 
## 安装和运行

1. 安装依赖：`pip install -r requirements.txt`
2. 初始化数据库：`python scripts/init_db.py`
3. 导入数据：`python scripts/import_words.py`
4. 启动服务：`uvicorn app.main:app --reload`

## API文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

```angular2html
english-graph-backend/         # 项目根目录
├── app/                       # 应用主目录
│   ├── __init__.py           # 使app成为Python包
│   ├── main.py               # FastAPI应用入口点，创建app实例和包含路由
│   ├── core/                 # 核心配置和工具
│   │   ├── __init__.py
│   │   ├── config.py         # 应用配置（数据库、安全等）
│   │   ├── security.py       # 认证和授权相关函数
│   │   └── dependencies.py   # 依赖注入（如获取当前用户）
│   ├── models/               # SQLModel数据模型定义
│   │   ├── __init__.py
│   │   ├── user.py           # 用户模型
│   │   ├── word.py           # 单词模型
│   │   ├── relation.py       # 关系模型
│   │   └── contribution.py   # 用户贡献模型
│   ├── schemas/              # Pydantic模式/序列化模型
│   │   ├── __init__.py
│   │   ├── user.py           # 用户相关的请求/响应模型
│   │   ├── word.py           # 单词相关的请求/响应模型
│   │   ├── relation.py       # 关系相关的请求/响应模型
│   │   └── contribution.py   # 贡献相关的请求/响应模型
│   ├── api/                  # API路由端点
│   │   ├── __init__.py
│   │   ├── endpoints/        # 各个端点的路由
│   │   │   ├── __init__.py
│   │   │   ├── auth.py       # 认证相关端点（登录、注册）
│   │   │   ├── words.py      # 单词相关端点
│   │   │   ├── relations.py  # 关系相关端点
│   │   │   ├── graph.py      # 图谱查询端点
│   │   │   ├── contributions.py # 用户贡献端点
│   │   │   └── admin.py      # 管理员审核端点
│   │   └── deps.py           # 路由依赖项
│   ├── crud/                 # 数据库CRUD操作
│   │   ├── __init__.py
│   │   ├── user.py           # 用户CRUD操作
│   │   ├── word.py           # 单词CRUD操作
│   │   ├── relation.py       # 关系CRUD操作
│   │   └── contribution.py   # 贡献CRUD操作
│   ├── services/             # 业务逻辑服务
│   │   ├── __init__.py
│   │   ├── auth.py           # 认证服务
│   │   ├── graph.py          # 图谱算法服务（BFS等）
│   │   └── import_data.py    # 数据导入服务
│   ├── database.py           # 数据库连接和引擎配置
│   └── utils/                # 工具函数
│       ├── __init__.py
│       ├── wechat.py         # 微信登录相关工具
│       └── validators.py     # 数据验证工具
├── tests/                    # 测试目录
│   ├── __init__.py
│   ├── conftest.py           # pytest配置和fixture
│   ├── test_api/             # API测试
│   └── test_services/        # 服务测试
├── scripts/                  # 脚本目录
│   ├── init_db.py           # 初始化数据库脚本
│   └── import_words.py      # 导入单词数据脚本
├── data/                     # 数据文件目录
│   └── oxford_3000.csv      # 牛津3000词表等原始数据
├── alembic/                  # 数据库迁移目录（可选）
│   ├── versions/            # 迁移脚本
│   └── env.py               # 迁移环境配置
├── requirements.txt          # Python依赖列表
├── .env                     # 环境变量（不提交到Git）
├── .gitignore
└── README.md                # 项目说明文档
```