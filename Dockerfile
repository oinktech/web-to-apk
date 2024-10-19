# 使用更小的 Alpine 镜像
FROM alpine:latest

# 设置环境变量
ENV ANDROID_HOME /opt/android-sdk
ENV PATH ${PATH}:${ANDROID_HOME}/cmdline-tools/tools/bin:${ANDROID_HOME}/platform-tools

# 安装基础工具和依赖项 (bash, curl, openjdk, node.js)
RUN apk update && apk add --no-cache \
    bash \
    curl \
    openjdk11 \
    nodejs \
    npm \
    unzip \
    git \
    python3 \
    py3-pip \
    build-base

# 安装 cordova 和其他工具
RUN npm install -g cordova

# 安装 Android SDK 工具（精简安装）
RUN mkdir -p /opt/android-sdk/cmdline-tools && \
    curl -o /tmp/sdk-tools.zip https://dl.google.com/android/repository/commandlinetools-linux-7583922_latest.zip && \
    unzip /tmp/sdk-tools.zip -d /opt/android-sdk/cmdline-tools && \
    rm /tmp/sdk-tools.zip && \
    yes | sdkmanager --licenses && \
    sdkmanager "platform-tools" "build-tools;30.0.3" "platforms;android-30"

# 清理临时文件
RUN rm -rf /var/cache/apk/* /tmp/*

# 创建工作目录
WORKDIR /usr/src/app

# 创建 uploads 目录
RUN mkdir -p uploads

# 复制当前目录的内容到容器
COPY . .

# 安装 Python 依赖项
RUN pip3 install -r requirements.txt

# 暴露 Flask 默认端口
EXPOSE 10000

# 启动 Flask 服务器
CMD ["python3", "app.py"]
