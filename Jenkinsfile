pipeline {
    agent any

    triggers {
        githubPush()
    }

    parameters {

        choice(
            name: 'BRANCH',
            choices: [
                'feature/jenkins-argocd-cicd',
                'main'
            ],
            description: 'Select the GitHub branch to build'
        )

        choice(
            name: 'ENVIRONMENT',
            choices: [
                'dev',
                'staging',
                'prod'
            ],
            description: 'Select the target environment'
        )

        choice(
            name: 'IMAGE_TAG',
            choices: [
                '1.0.0',
                '1.0.1',
                '1.0.2'
            ],
            description: 'Select the Docker image version'
        )

        booleanParam(
            name: 'RUN_TESTS',
            defaultValue: true,
            description: 'Run Maven tests'
        )

        booleanParam(
            name: 'PUSH_IMAGE',
            defaultValue: true,
            description: 'Push Docker image to Docker Hub'
        )
    }

    environment {

        // GitHub
        GITHUB_REPO = 'https://github.com/manjunath031984/Employment-Management.git'
        GITHUB_CREDENTIALS = 'github-pat'

        // Docker Hub
        DOCKER_IMAGE = 'vannalmanju/employment-management'
        DOCKER_CREDENTIALS = 'dockerhub-pat'
        DOCKER_REGISTRY = 'docker.io'

        // Application
        APP_NAME = 'employment-management'
    }

    stages {

        /*
         * ==========================================
         * ENVIRONMENT CHECK
         * ==========================================
         */
        stage('Environment Check') {
            steps {

                echo '''
==========================================
        EMPLOYMENT MANAGEMENT CI/CD
==========================================
'''

                echo "Build Number : ${env.BUILD_NUMBER}"
                echo "Branch       : ${params.BRANCH}"
                echo "Environment  : ${params.ENVIRONMENT}"
                echo "Image Tag    : ${params.IMAGE_TAG}"
                echo "Run Tests    : ${params.RUN_TESTS}"
                echo "Push Image   : ${params.PUSH_IMAGE}"
                echo "Docker Image : ${env.DOCKER_IMAGE}:${params.IMAGE_TAG}"

                sh '''
                    echo "=========================================="
                    echo "Agent Information"
                    echo "=========================================="

                    echo "Hostname:"
                    hostname

                    echo ""
                    echo "Java Version:"
                    java -version || true

                    echo ""
                    echo "Maven Version:"
                    mvn -version || true

                    echo ""
                    echo "Docker Version:"
                    docker --version || true

                    echo ""
                    echo "Git Version:"
                    git --version || true
                '''
            }
        }


        /*
         * ==========================================
         * CHECKOUT GIT REPOSITORY
         * ==========================================
         */
        stage('Checkout Git Repository') {

            steps {

                echo "=========================================="
                echo "CHECKOUT GIT REPOSITORY"
                echo "=========================================="

                echo "Repository : ${env.GITHUB_REPO}"
                echo "Branch     : ${params.BRANCH}"

                checkout([
                    $class: 'GitSCM',

                    branches: [
                        [
                            name: "*/${params.BRANCH}"
                        ]
                    ],

                    userRemoteConfigs: [
                        [
                            url: env.GITHUB_REPO,
                            credentialsId: env.GITHUB_CREDENTIALS
                        ]
                    ],

                    extensions: [
                        [
                            $class: 'CleanBeforeCheckout'
                        ]
                    ]
                ]

                sh '''
                    echo "=========================================="
                    echo "Git Information"
                    echo "=========================================="

                    git branch --show-current || true
                    git log -1 --oneline
                    git status --short
                '''
            }
        }


        /*
         * ==========================================
         * MAVEN BUILD
         * ==========================================
         */
        stage('Maven Build') {

            steps {

                echo "=========================================="
                echo "MAVEN BUILD"
                echo "=========================================="

                sh '''
                    echo "Building Spring Boot application..."

                    if [ -f "./mvnw" ]; then
                        chmod +x ./mvnw
                        ./mvnw clean package -DskipTests
                    else
                        mvn clean package -DskipTests
                    fi

                    echo ""
                    echo "Maven build completed successfully."

                    echo ""
                    echo "Generated artifacts:"
                    find target -maxdepth 1 -type f 2>/dev/null || true
                '''
            }
        }


        /*
         * ==========================================
         * MAVEN TEST
         * ==========================================
         */
        stage('Maven Test') {

            when {
                expression {
                    return params.RUN_TESTS
                }
            }

            steps {

                echo "=========================================="
                echo "MAVEN TEST"
                echo "=========================================="

                sh '''
                    echo "Running Maven tests..."

                    if [ -f "./mvnw" ]; then
                        ./mvnw test
                    else
                        mvn test
                    fi

                    echo ""
                    echo "All Maven tests completed successfully."
                '''
            }
        }


        /*
         * ==========================================
         * DOCKER BUILD
         * ==========================================
         */
        stage('Docker Build') {

            steps {

                script {

                    def imageTag = params.IMAGE_TAG

                    if (!imageTag?.trim()) {
                        error("Docker image tag is empty. Please select a valid IMAGE_TAG.")
                    }

                    def fullImageName =
                        "${env.DOCKER_IMAGE}:${imageTag}"

                    echo "=========================================="
                    echo "DOCKER BUILD"
                    echo "=========================================="

                    echo "Docker Image : ${env.DOCKER_IMAGE}"
                    echo "Image Tag    : ${imageTag}"
                    echo "Full Image   : ${fullImageName}"

                    sh """
                        echo "Docker version:"
                        docker --version

                        echo ""
                        echo "Building Docker image..."

                        docker build \\
                            -t "${fullImageName}" \\
                            .

                        echo ""
                        echo "Docker image built successfully."

                        echo ""
                        echo "Docker image:"
                        docker images "${env.DOCKER_IMAGE}" --format "table {{.Repository}}\\t{{.Tag}}\\t{{.ID}}\\t{{.Size}}"
                    """
                }
            }
        }


        /*
         * ==========================================
         * DOCKER IMAGE VALIDATION
         * ==========================================
         */
        stage('Docker Image Validation') {

            steps {

                script {

                    def fullImageName =
                        "${env.DOCKER_IMAGE}:${params.IMAGE_TAG}"

                    echo "=========================================="
                    echo "DOCKER IMAGE VALIDATION"
                    echo "=========================================="

                    sh """
                        echo "Checking image: ${fullImageName}"

                        docker image inspect "${fullImageName}" > /dev/null

                        echo ""
                        echo "Image exists successfully."

                        echo ""
                        echo "Image details:"
                        docker image inspect "${fullImageName}" \\
                            --format='Repository: {{index .RepoTags 0}}
Image ID: {{.Id}}
Size: {{.Size}}'
                    """
                }
            }
        }


        /*
         * ==========================================
         * INPUT / MANUAL APPROVAL
         * ==========================================
         */
        stage('Approval for Docker Hub Push') {

            when {
                expression {
                    return params.PUSH_IMAGE
                }
            }

            steps {

                script {

                    def fullImageName =
                        "${env.DOCKER_IMAGE}:${params.IMAGE_TAG}"

                    input(
                        message: """
==========================================

Docker image is ready.

Image:
${fullImageName}

Environment:
${params.ENVIRONMENT}

Branch:
${params.BRANCH}

Do you want to push this image to Docker Hub?

==========================================
""",
                        ok: 'Approve & Push Image'
                    )
                }
            }
        }


        /*
         * ==========================================
         * DOCKER HUB LOGIN
         * ==========================================
         */
        stage('Docker Hub Login') {

            when {
                expression {
                    return params.PUSH_IMAGE
                }
            }

            steps {

                echo "=========================================="
                echo "DOCKER HUB LOGIN"
                echo "=========================================="

                withCredentials([
                    usernamePassword(
                        credentialsId: env.DOCKER_CREDENTIALS,
                        usernameVariable: 'DOCKER_USERNAME',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )
                ]) {

                    sh '''
                        echo "$DOCKER_PASSWORD" | \
                        docker login \
                        --username "$DOCKER_USERNAME" \
                        --password-stdin

                        echo ""
                        echo "Docker Hub authentication successful."
                    '''
                }
            }
        }


        /*
         * ==========================================
         * PUSH TO DOCKER HUB
         * ==========================================
         */
        stage('Push to Docker Hub') {

            when {
                expression {
                    return params.PUSH_IMAGE
                }
            }

            steps {

                script {

                    def fullImageName =
                        "${env.DOCKER_IMAGE}:${params.IMAGE_TAG}"

                    echo "=========================================="
                    echo "PUSH TO DOCKER HUB"
                    echo "=========================================="

                    echo "Pushing:"
                    echo "${fullImageName}"

                    sh """
                        docker push "${fullImageName}"

                        echo ""
                        echo "Docker image pushed successfully."

                        echo ""
                        echo "Published Image:"
                        echo "${fullImageName}"
                    """
                }
            }
        }


        /*
         * ==========================================
         * DOCKER LOGOUT
         * ==========================================
         */
        stage('Docker Hub Logout') {

            when {
                expression {
                    return params.PUSH_IMAGE
                }
            }

            steps {

                sh '''
                    docker logout || true

                    echo "Docker Hub logout completed."
                '''
            }
        }


        /*
         * ==========================================
         * PIPELINE SUMMARY
         * ==========================================
         */
        stage('Pipeline Summary') {

            steps {

                echo """
==========================================
        PIPELINE SUMMARY
==========================================

Application     : ${env.APP_NAME}
Git Branch      : ${params.BRANCH}
Environment     : ${params.ENVIRONMENT}

Docker Image    : ${env.DOCKER_IMAGE}
Docker Tag      : ${params.IMAGE_TAG}

Full Image      : ${env.DOCKER_IMAGE}:${params.IMAGE_TAG}

Build Number    : ${env.BUILD_NUMBER}

==========================================
"""
            }
        }
    }


    /*
     * ==========================================
     * POST ACTIONS
     * ==========================================
     */
    post {

        success {

            echo """
==========================================
        PIPELINE SUCCESSFUL
==========================================

Build Number : ${env.BUILD_NUMBER}
Branch       : ${params.BRANCH}
Environment  : ${params.ENVIRONMENT}

Docker Image :
${env.DOCKER_IMAGE}:${params.IMAGE_TAG}

==========================================
"""
        }

        failure {

            echo """
==========================================
        PIPELINE FAILED
==========================================

Build Number : ${env.BUILD_NUMBER}
Branch       : ${params.BRANCH}

Please check the Jenkins console log.

==========================================
"""
        }

        aborted {

            echo """
==========================================
        PIPELINE ABORTED
==========================================

Build Number : ${env.BUILD_NUMBER}

==========================================
"""
        }

        always {

            echo "Pipeline execution completed."
        }
    }
}