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

        GITHUB_REPO = 'https://github.com/manjunath031984/Employment-Management.git'
        GITHUB_CREDENTIALS = 'github-pat'

        DOCKER_IMAGE = 'vannalmanju/employment-management'
        DOCKER_CREDENTIALS = 'dockerhub-pat'

        APP_NAME = 'employment-management'
    }

    stages {

        // =====================================================
        // 1. ENVIRONMENT CHECK
        // =====================================================

        stage('Environment Check') {

            steps {

                echo '=========================================='
                echo 'EMPLOYMENT MANAGEMENT CI/CD'
                echo '=========================================='

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
                    echo "Java:"
                    java -version || true

                    echo ""
                    echo "Maven:"
                    mvn -version || true

                    echo ""
                    echo "Docker:"
                    docker --version

                    echo ""
                    echo "Git:"
                    git --version
                '''
            }
        }


        // =====================================================
        // 2. CHECKOUT GIT REPOSITORY
        // =====================================================

        stage('Checkout Git Repository') {

            steps {

                echo '=========================================='
                echo 'CHECKOUT GIT REPOSITORY'
                echo '=========================================='

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
                ])

                sh '''
                    echo "=========================================="
                    echo "Git Information"
                    echo "=========================================="

                    git branch --show-current

                    echo ""
                    echo "Latest commit:"
                    git log -1 --oneline

                    echo ""
                    echo "Git status:"
                    git status --short
                '''
            }
        }


        // =====================================================
        // 3. MAVEN BUILD
        // =====================================================

        stage('Maven Build') {

            steps {

                echo '=========================================='
                echo 'MAVEN BUILD'
                echo '=========================================='

                sh '''
                    echo "Starting Maven build..."

                    if [ -f "./mvnw" ]; then
                        chmod +x ./mvnw
                        ./mvnw clean package -DskipTests
                    else
                        mvn clean package -DskipTests
                    fi

                    echo ""
                    echo "Maven build completed successfully."

                    echo ""
                    echo "Build artifacts:"
                    find target -maxdepth 1 -type f 2>/dev/null || true
                '''
            }
        }


        // =====================================================
        // 4. MAVEN TEST
        // =====================================================

        stage('Maven Test') {

            when {
                expression {
                    return params.RUN_TESTS
                }
            }

            steps {

                echo '=========================================='
                echo 'MAVEN TEST'
                echo '=========================================='

                sh '''
                    echo "Running Maven tests..."

                    if [ -f "./mvnw" ]; then
                        ./mvnw test
                    else
                        mvn test
                    fi

                    echo ""
                    echo "Maven tests completed successfully."
                '''
            }
        }


        // =====================================================
        // 5. DOCKER BUILD
        // =====================================================

        stage('Docker Build') {

            steps {

                script {

                    if (!params.IMAGE_TAG?.trim()) {
                        error('IMAGE_TAG cannot be empty.')
                    }

                    def fullImageName =
                        "${env.DOCKER_IMAGE}:${params.IMAGE_TAG}"

                    echo '=========================================='
                    echo 'DOCKER BUILD'
                    echo '=========================================='

                    echo "Docker Image : ${env.DOCKER_IMAGE}"
                    echo "Image Tag    : ${params.IMAGE_TAG}"
                    echo "Full Image   : ${fullImageName}"

                    sh """
                        echo "Docker version:"
                        docker --version

                        echo ""
                        echo "Building Docker image..."

                        docker build -t ${fullImageName} .

                        echo ""
                        echo "Docker image built successfully."

                        echo ""
                        echo "Created image:"
                        docker images ${env.DOCKER_IMAGE}
                    """
                }
            }
        }


        // =====================================================
        // 6. DOCKER IMAGE VALIDATION
        // =====================================================

        stage('Docker Image Validation') {

            steps {

                script {

                    def fullImageName =
                        "${env.DOCKER_IMAGE}:${params.IMAGE_TAG}"

                    echo '=========================================='
                    echo 'DOCKER IMAGE VALIDATION'
                    echo '=========================================='

                    echo "Validating image:"
                    echo fullImageName

                    sh """
                        docker image inspect ${fullImageName} > /dev/null

                        echo "Docker image exists successfully."

                        echo ""
                        echo "Image information:"
                        docker image inspect ${fullImageName} --format='ID: {{.Id}}'
                    """
                }
            }
        }


        // =====================================================
        // 7. MANUAL INPUT APPROVAL
        // =====================================================

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

                    echo '=========================================='
                    echo 'MANUAL APPROVAL REQUIRED'
                    echo '=========================================='

                    input(
                        message: """
Docker image is ready.

Image:
${fullImageName}

Environment:
${params.ENVIRONMENT}

Branch:
${params.BRANCH}

Do you want to push this image to Docker Hub?
""",
                        ok: 'Approve & Push Image'
                    )
                }
            }
        }


        // =====================================================
        // 8. DOCKER HUB LOGIN
        // =====================================================

        stage('Docker Hub Login') {

            when {
                expression {
                    return params.PUSH_IMAGE
                }
            }

            steps {

                echo '=========================================='
                echo 'DOCKER HUB LOGIN'
                echo '=========================================='

                withCredentials([
                    usernamePassword(
                        credentialsId: env.DOCKER_CREDENTIALS,
                        usernameVariable: 'DOCKER_USERNAME',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )
                ]) {

                    sh '''
                        echo "$DOCKER_PASSWORD" | docker login \
                            --username "$DOCKER_USERNAME" \
                            --password-stdin

                        echo ""
                        echo "Docker Hub login successful."
                    '''
                }
            }
        }


        // =====================================================
        // 9. PUSH TO DOCKER HUB
        // =====================================================

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

                    echo '=========================================='
                    echo 'PUSH TO DOCKER HUB'
                    echo '=========================================='

                    echo "Pushing image:"
                    echo fullImageName

                    sh """
                        docker push ${fullImageName}

                        echo ""
                        echo "Docker image pushed successfully."
                        echo ""
                        echo "Published image:"
                        echo "${fullImageName}"
                    """
                }
            }
        }


        // =====================================================
        // 10. DOCKER LOGOUT
        // =====================================================

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


        // =====================================================
        // 11. PIPELINE SUMMARY
        // =====================================================

        stage('Pipeline Summary') {

            steps {

                echo '=========================================='
                echo 'PIPELINE SUMMARY'
                echo '=========================================='

                echo "Application  : ${env.APP_NAME}"
                echo "Branch       : ${params.BRANCH}"
                echo "Environment  : ${params.ENVIRONMENT}"
                echo "Image        : ${env.DOCKER_IMAGE}:${params.IMAGE_TAG}"
                echo "Build Number : ${env.BUILD_NUMBER}"

                echo '=========================================='
            }
        }
    }


    // =========================================================
    // POST ACTIONS
    // =========================================================

    post {

        success {

            echo '=========================================='
            echo 'PIPELINE SUCCESSFUL'
            echo '=========================================='

            echo "Build Number : ${env.BUILD_NUMBER}"
            echo "Branch       : ${params.BRANCH}"
            echo "Environment  : ${params.ENVIRONMENT}"
            echo "Docker Image : ${env.DOCKER_IMAGE}:${params.IMAGE_TAG}"

            echo '=========================================='
        }

        failure {

            echo '=========================================='
            echo 'PIPELINE FAILED'
            echo '=========================================='

            echo "Build Number : ${env.BUILD_NUMBER}"
            echo "Branch       : ${params.BRANCH}"

            echo 'Please check the Jenkins console output.'

            echo '=========================================='
        }

        aborted {

            echo '=========================================='
            echo 'PIPELINE ABORTED'
            echo '=========================================='
        }

        always {

            echo 'Pipeline execution completed.'
        }
    }
}