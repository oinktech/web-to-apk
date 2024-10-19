# 使用更小的 Alpine 镜像
FROM openjdk:11-jre-slim

# 设置环境变量
ENV ANDROID_HOME /opt/android-sdk
ENV PATH ${PATH}:${ANDROID_HOME}/cmdline-tools/latest/bin:${ANDROID_HOME}/platform-tools

# 安装基础工具和依赖项
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    unzip \
    npm \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# 安装 Cordova
RUN npm install -g cordova

# 安装 Android SDK 工具
RUN mkdir -p ${ANDROID_HOME}/cmdline-tools && \
    curl -o /tmp/sdk-tools.zip https://dl.google.com/android/repository/commandlinetools-linux-7583922_latest.zip && \
    unzip /tmp/sdk-tools.zip -d ${ANDROID_HOME}/cmdline-tools && \
    rm /tmp/sdk-tools.zip && \
    mv ${ANDROID_HOME}/cmdline-tools/cmdline-tools ${ANDROID_HOME}/cmdline-tools/latest && \
    yes | sdkmanager --licenses && \
    sdkmanager "platform-tools" "build-tools;30.0.3" "platforms;android-30" && \
    rm -rf ${ANDROID_HOME}/cmdline-tools/latest/bin/sdkmanager

# 创建工作目录
WORKDIR /usr/src/app

# 创建 uploads 目录
RUN mkdir -p uploads

# 复制当前目录的内容到容器
COPY . .

# 安装 Python 依赖项
RUN pip3 install --no-cache-dir -r requirements.txt

# 暴露 Flask 默认端口
EXPOSE 10000

# 启动 Flask 服务器
CMD ["python3", "app.py"]
