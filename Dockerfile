# Use smaller Alpine image
FROM alpine:latest

# Set environment variables
ENV ANDROID_HOME /opt/android-sdk
ENV PATH ${PATH}:${ANDROID_HOME}/cmdline-tools/tools/bin:${ANDROID_HOME}/platform-tools

# Install base tools and dependencies (bash, curl, openjdk, node.js)
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

# Install cordova and other tools
RUN npm install -g cordova

# Install Android SDK tools (minimal installation)
RUN mkdir -p /opt/android-sdk/cmdline-tools && \
    curl -o /tmp/sdk-tools.zip https://dl.google.com/android/repository/commandlinetools-linux-7583922_latest.zip && \
    unzip /tmp/sdk-tools.zip -d /opt/android-sdk/cmdline-tools && \
    rm /tmp/sdk-tools.zip && \
    yes | sdkmanager --licenses && \
    sdkmanager "platform-tools" "build-tools;30.0.3" "platforms;android-30"

# Clean up temporary files
RUN rm -rf /var/cache/apk/* /tmp/*

# Create working directory
WORKDIR /usr/src/app

# Copy current directory contents to container
COPY . .

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Expose Flask default port
EXPOSE 10000

# Start Flask server
CMD ["python3", "app.py"]
