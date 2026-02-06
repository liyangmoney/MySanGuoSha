# 使用官方Python运行时作为基础镜像
FROM python:3.9-slim

# 安装必要的系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制项目文件到工作目录
COPY requirements.txt /app/requirements.txt

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制整个项目
COPY . /app/

# 暴露端口
EXPOSE 5000

# 启动命令 - 使用eventlet运行app.py
CMD ["python", "app.py"]