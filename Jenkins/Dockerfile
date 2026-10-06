# ============================================================
# Jenkins Custom Image
# Employment Management CI/CD
# ============================================================

FROM jenkins/jenkins:lts-jdk21

USER root


# ============================================================
# Base Packages
# ============================================================

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        wget \
        unzip \
        zip \
        git \
        vim \
        nano \
        jq \
        gnupg \
        lsb-release \
        python3 \
        python3-pip \
        python3-venv \
        maven \
        openssh-client \
        rsync \
        procps \
        net-tools \
        iputils-ping \
        dnsutils \
        awscli \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


# ============================================================
# Docker CLI
# ============================================================

RUN install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL \
      https://download.docker.com/linux/debian/gpg \
      -o /etc/apt/keyrings/docker.asc && \
    chmod a+r /etc/apt/keyrings/docker.asc && \
    echo \
      "deb [arch=$(dpkg --print-architecture) \
      signed-by=/etc/apt/keyrings/docker.asc] \
      https://download.docker.com/linux/debian \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
      > /etc/apt/sources.list.d/docker.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
      docker-ce-cli && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


# ============================================================
# Terraform
# ============================================================

ARG TERRAFORM_VERSION=1.13.2

RUN curl -fsSL \
      "https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip" \
      -o /tmp/terraform.zip && \
    unzip -o /tmp/terraform.zip -d /usr/local/bin && \
    rm -f /tmp/terraform.zip


# ============================================================
# kubectl
# ============================================================

ARG KUBECTL_MINOR=v1.34

RUN install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL \
      "https://pkgs.k8s.io/core:/stable:/${KUBECTL_MINOR}/deb/Release.key" \
      | gpg --dearmor \
      -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg && \
    chmod 0644 /etc/apt/keyrings/kubernetes-apt-keyring.gpg && \
    echo \
      "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] \
      https://pkgs.k8s.io/core:/stable:/${KUBECTL_MINOR}/deb/ /" \
      > /etc/apt/sources.list.d/kubernetes.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends kubectl && \
    apt-mark hold kubectl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


# ============================================================
# Helm
# ============================================================

ARG HELM_VERSION=v3.19.0

RUN curl -fsSL \
      "https://get.helm.sh/helm-${HELM_VERSION}-linux-amd64.tar.gz" \
      -o /tmp/helm.tar.gz && \
    tar -zxvf /tmp/helm.tar.gz -C /tmp && \
    mv /tmp/linux-amd64/helm /usr/local/bin/helm && \
    chmod +x /usr/local/bin/helm && \
    rm -rf /tmp/helm.tar.gz /tmp/linux-amd64


# ============================================================
# Verify Required Tools
# ============================================================

RUN echo "============================================" && \
    echo "Java" && \
    java -version && \
    echo "============================================" && \
    echo "Maven" && \
    mvn --version && \
    echo "============================================" && \
    echo "Git" && \
    git --version && \
    echo "============================================" && \
    echo "Docker CLI" && \
    docker --version && \
    echo "============================================" && \
    echo "AWS CLI" && \
    aws --version && \
    echo "============================================" && \
    echo "Terraform" && \
    terraform version && \
    echo "============================================" && \
    echo "kubectl" && \
    kubectl version --client && \
    echo "============================================" && \
    echo "Helm" && \
    helm version && \
    echo "============================================"


# ============================================================
# Jenkins Plugins
# ============================================================

COPY plugins.txt /usr/share/jenkins/ref/plugins.txt

RUN jenkins-plugin-cli \
      --plugin-file /usr/share/jenkins/ref/plugins.txt


# ============================================================
# Jenkins Permissions
# ============================================================

RUN chown -R jenkins:jenkins /usr/share/jenkins/ref


# ============================================================
# Switch Back to Jenkins User
# ============================================================

USER jenkins