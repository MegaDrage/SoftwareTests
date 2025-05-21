FROM jenkins/jenkins:lts-alpine-jdk21

USER root

RUN apk add --no-cache \
    wget \
    curl \
    unzip \
    curl \
    qemu-system-arm \
    docker-cli-buildx \
    docker-cli \
    bash \
    shadow \
    && rm -rf /var/cache/apk/* \
    && su jenkins \
    && jenkins-plugin-cli --plugins "blueocean docker-workflow git-parameter"