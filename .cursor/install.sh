#!/usr/bin/env bash
# Idempotent Cloud Agent setup for the Employment Management Spring Boot app.
# The default base image already provides Java 21 and git/curl; this script
# adds Apache Maven (not present by default) and warms the build.
set -euo pipefail

MAVEN_VERSION="3.9.9"
MAVEN_HOME="/opt/apache-maven-${MAVEN_VERSION}"

if ! command -v mvn >/dev/null 2>&1; then
  echo "Installing Apache Maven ${MAVEN_VERSION}..."
  tmp_dir="$(mktemp -d)"
  curl -fsSL -o "${tmp_dir}/maven.tar.gz" \
    "https://archive.apache.org/dist/maven/maven-3/${MAVEN_VERSION}/binaries/apache-maven-${MAVEN_VERSION}-bin.tar.gz"
  sudo tar -xzf "${tmp_dir}/maven.tar.gz" -C /opt
  sudo ln -sf "${MAVEN_HOME}/bin/mvn" /usr/local/bin/mvn
  rm -rf "${tmp_dir}"
fi

java -version
mvn -version

# Resolve dependencies and produce the runnable jar consumed by the app terminal.
mvn -B -DskipTests clean package
