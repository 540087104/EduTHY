# EduTHY · 教学智能体（AI 智能答疑）

基于 Django 的课程智能答疑系统。学生通过聊天界面提问，系统利用 AI 语义匹配引擎从课程知识库中自动检索最佳答案，实现 7×24 小时智能答疑。

## 一、功能说明

本项目选择的 AI 功能点是 **「智能答疑（AI Question & Answer）」**。

### 1. 为什么加入 AI 后效果更好？

传统的答疑系统通常采用**关键词精确匹配**：学生必须用预设的措辞提问才能命中答案，一旦换一种说法（如把"如何查看当前目录"说成"怎么查看我现在在哪个文件夹"）就匹配失败。

加入 AI 语义匹配后，效果显著提升：

| 对比维度 | 传统关键词匹配 | AI 语义匹配（本项目） |
|---------|--------------|---------------------|
| 匹配方式 | 必须包含预设关键词 | 二元组 + 单字 + 关键词综合相似度 |
| 措辞容错 | 差，换说法就失败 | 好，"如何查看目录"与"怎么查看当前所在的目录"都能命中 |
| 未命中处理 | 直接返回空 | 给出兜底提示，并记录问题供教师补充题库 |
| 体验 | 僵硬，像查字典 | 自然，像和助教对话 |

本项目的 AI 匹配引擎采用**轻量级语义匹配**（不依赖外部大模型 API）：
- **中文二元组（bigram）相似度**：捕捉词语局部语义
- **单字重合度**：捕捉跨词语义重合
- **关键词重合度**：利用教师标注的关键词加权
- 综合得分超过阈值即命中，否则走兜底回答

### 2. 数据库表结构

共 4 张核心表（位于 `AIQandA/models.py`）：

#### Course（课程表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BigAutoField | 主键 |
| name | CharField(100) | 课程名称 |
| description | TextField | 课程描述 |
| created_at | DateTimeField | 创建时间 |

#### Chapter（章节表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BigAutoField | 主键 |
| course | ForeignKey → Course | 所属课程 |
| title | CharField(200) | 章节标题 |
| order | IntegerField | 章节顺序 |
| content | TextField | 章节内容 |

#### QuestionAnswerPair（问答对表，知识库核心）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BigAutoField | 主键 |
| chapter | ForeignKey → Chapter | 所属章节 |
| question | TextField | 标准问题 |
| answer | TextField | 标准答案 |
| keywords | CharField(255) | 关键词（逗号分隔） |
| is_active | BooleanField | 是否启用 |

#### ChatHistory（对话历史表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BigAutoField | 主键 |
| user | ForeignKey → User (可空) | 提问用户 |
| session_key | CharField(40) | 会话标识 |
| question | TextField | 用户提问 |
| matched_qa | ForeignKey → QuestionAnswerPair (可空) | 命中的问答对 |
| answer | TextField | 系统回答 |
| is_helpful | BooleanField (可空) | 是否有帮助 |
| created_at | DateTimeField | 提问时间 |

## 二、项目结构

```
EduTHY/
├── AIQandA/                    # 智能答疑 APP
│   ├── management/commands/    # 种子数据命令
│   │   └── seed_data.py        # 灌入示例问答对
│   ├── migrations/             # 数据库迁移
│   ├── templates/AIQandA/      # 聊天页面模板
│   │   └── chat.html
│   ├── admin.py                # 后台注册
│   ├── apps.py
│   ├── models.py               # 数据模型
│   ├── services.py             # AI 匹配引擎
│   ├── tests.py                # 单元测试
│   ├── urls.py                 # 路由
│   └── views.py                # 视图
├── EduTHY/                     # 项目配置
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── deploy/                     # 部署配置
│   ├── nginx.conf              # nginx 反向代理配置
│   └── gunicorn.service        # gunicorn systemd 服务
├── manage.py
├── requirements.txt
├── pyproject.toml
├── Makefile
└── README.md
```

## 三、快速开始

### 环境要求
- Python 3.10+
- pip

### 安装与运行

```bash
# 1. 克隆项目
git clone <仓库地址>
cd EduTHY

# 2. 创建虚拟环境并安装依赖
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
make install                    # pip install -r requirements.txt

# 3. 数据库迁移 + 灌入示例数据
make migrate
make seed                       # python manage.py seed_data

# 4. 启动开发服务器
make run                        # python manage.py runserver 0.0.0.0:8000
```

浏览器访问 `http://127.0.0.1:8000/` 即可使用智能答疑。

### 管理后台

```bash
python manage.py createsuperuser
```
访问 `http://127.0.0.1:8000/admin/` 可管理课程、章节、问答对。

## 四、Makefile 命令

| 命令 | 说明 |
|------|------|
| `make install` | 安装依赖 |
| `make lint` | pylint 代码检查 |
| `make test` | pytest 单元测试 |
| `make format` | black 代码格式化 |
| `make run` | 启动开发服务器 |
| `make migrate` | 执行数据库迁移 |
| `make seed` | 灌入示例问答数据 |

## 五、部署到云主机（Linux）

### 1. 修改主机名

```bash
# 将 YOUR_NAME 替换为你的姓名全拼，例如 tianhaoyu
sudo hostnamectl set-hostname tianhaoyu
# 验证
hostname
```

### 2. 安装 nginx

```bash
sudo yum install -y nginx        # Alibaba Cloud Linux / CentOS
# 或 sudo apt install -y nginx   # Ubuntu
sudo systemctl enable --now nginx
```

### 3. 部署 Django 项目

```bash
# 安装 Python 与虚拟环境
sudo yum install -y python3 python3-pip python3-devel

# 拉取代码
cd /home
sudo git clone <仓库地址> EduTHY
cd /home/EduTHY

# 创建虚拟环境并安装依赖
python3 -m venv venv
source venv/bin/activate
make install

# 迁移 + 收集静态文件 + 灌数据
make migrate
python manage.py collectstatic --noinput
make seed
```

### 4. 配置 gunicorn（systemd 服务）

```bash
sudo cp deploy/gunicorn.service /etc/systemd/system/eduthy.service
sudo systemctl daemon-reload
sudo systemctl enable --now eduthy
sudo systemctl status eduthy
```

### 5. 配置 nginx 反向代理

```bash
sudo cp deploy/nginx.conf /etc/nginx/conf.d/eduthy.conf
sudo nginx -t
sudo systemctl reload nginx
```

### 6. 开放安全组端口

在云控制台安全组中放行 **80 端口**（HTTP）。

### 7. 访问验证

浏览器访问 `http://<云主机公网IP>/` 即可看到智能答疑页面。

## 六、技术栈

- **后端框架**：Django 6.1
- **AI 引擎**：自研轻量级语义匹配（二元组 + 单字 + 关键词 Jaccard 相似度）
- **生产服务器**：gunicorn + nginx
- **代码质量**：pylint、black、pytest、pytest-django
