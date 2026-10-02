pipeline {
    agent any

    parameters {

        choice(
            name: 'ENVIRONMENT',
            choices: [
                'dev',
                'staging',
                'prod'
            ],
            description: 'Select the deployment environment'
        )

        string(
            name: 'BRANCH',
            defaultValue: 'feature/jenkins-argocd-cicd',
            description: 'Git branch to build'
        )

        choice(
            name: 'IMAGE_TAG',
            choices: [
                '1.0.0',
                '1.0.1',
                '1.0.2'
            ],
            description: 'Select Docker image tag'
        )

        booleanParam(
            name: 'RUN_TESTS',
            defaultValue: true,
            description: 'Run Maven tests'
        )
    }

    environment {

        // GitHub
        GITHUB_REPO = 'https://github.com/manjunath031984/Employment-Management.git'

        // Docker Hub
        DOCKERHUB_USERNAME = 'vannalmanju'
        DOCKER_IMAGE = 'vannalmanju/employment-management'

        // Jenkins Credentials
        GITHUB_CREDENTIALS = 'github-pat'
        DOCKER_CREDENTIALS = 'dockerhub-pat'
    }

    stages {

        /*
         * ============================================================
         * 1. ENVIRONMENT CHECK
         * ============================================================
         */
        stage('Environment Check') {
            steps {
                echo '=========================================='
                echo '       ENVIRONMENT CONFIGURATION'
                echo '=========================================='
                echo "Environment : ${params.ENVIRONMENT}"
                echo "Branch      : ${params.BRANCH}"
                echo "Image Tag   : ${params.IMAGE_TAG}"
                echo "Run Tests   : ${params.RUN_TESTS}"
                echo "Docker Image: ${env.DOCKER_IMAGE}:${params.IMAGE_TAG}"
                echo '=========================================='
            }
        }

        /*
         * ============================================================
         * 2. CHECKOUT GIT REPOSITORY
         * ============================================================
         */
        stage('Checkout Git Repo') {
            steps {

                echo '=========================================='
                echo '       CHECKOUT GIT REPOSITORY'
                echo '=========================================='

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
                    ]
                ])

                sh '''
                    echo "Git checkout completed"
                    echo "Current branch:"
                    git branch --show-current

                    echo "Latest commit:"
                    git log -1 --oneline
                '''
            }
        }

        /*
         * ============================================================
         * 3. MAVEN BUILD
         * ============================================================
         */
        stage('Maven Build') {
            steps {

                echo '=========================================='
                echo '              MAVEN BUILD'
                echo '=========================================='

                sh '''
                    echo "Java version:"
                    java -version

                    echo ""
                    echo "Maven version:"
                    mvn -version

                    echo ""
                    echo "Starting Maven build..."
                '''

                script {

                    if (params.RUN_TESTS) {

                        sh '''
                            echo "Running Maven build and tests..."
                            mvn clean package
                        '''

                    } else {

                        sh '''
                            echo "Running Maven build without tests..."
                            mvn clean package -DskipTests
                        '''
                    }
                }

                echo 'Maven build completed successfully'
            }
        }

        /*
         * ============================================================
         * 4. DOCKER BUILD
         * ============================================================
         */
        stage('Docker Build') {
            steps {

                echo '=========================================='
                echo '             DOCKER BUILD'
                echo '=========================================='

                echo "Docker Image : ${env.DOCKER_IMAGE}"
                echo "Image Tag    : ${params.IMAGE_TAG}"

                sh '''
                    echo "Docker version:"
                    docker --version

                    echo ""
                    echo "Building Docker image..."

                    docker build \
                        -t "${DOCKER_IMAGE}:${IMAGE_TAG}" \
                        .

                    echo ""
                    echo "Docker image created successfully"

                    docker images "${DOCKER_IMAGE}"
                '''
            }
        }

        /*
         * ============================================================
         * 5. DOCKER HUB INPUT REQUEST
         * ============================================================
         */
        stage('Docker Hub Input Request') {
            steps {

                script {

                    def pushImage = input(
                        message: 'Do you want to push the Docker image to Docker Hub?',
                        ok: 'Submit',
                        parameters: [
                            booleanParam(
                                name: 'PUSH_IMAGE',
                                defaultValue: true,
                                description: 'Select YES to push the Docker image to Docker Hub'
                            )
                        ]
                    )

                    env.PUSH_IMAGE = pushImage.toString()

                    echo "Docker Hub Push Decision: ${env.PUSH_IMAGE}"
                }
            }
        }

        /*
         * ============================================================
         * 6. DOCKER HUB LOGIN
         * ============================================================
         */
        stage('Docker Hub Login') {
            when {
                expression {
                    env.PUSH_IMAGE == 'true'
                }
            }

            steps {

                echo '=========================================='
                echo '             DOCKER HUB LOGIN'
                echo '=========================================='

                withCredentials([
                    usernamePassword(
                        credentialsId: env.DOCKER_CREDENTIALS,
                        usernameVariable: 'DOCKER_USERNAME',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )
                ]) {

                    sh '''
                        echo "Logging into Docker Hub..."

                        echo "$DOCKER_PASSWORD" | docker login \
                            --username "$DOCKER_USERNAME" \
                            --password-stdin

                        echo "Docker Hub login successful"
                    '''
                }
            }
        }

        /*
         * ============================================================
         * 7. PUSH IMAGE TO DOCKER HUB
         * ============================================================
         */
        stage('Push to Docker Hub') {
            when {
                expression {
                    env.PUSH_IMAGE == 'true'
                }
            }

            steps {

                echo '=========================================='
                echo '          PUSH TO DOCKER HUB'
                echo '=========================================='

                sh '''
                    echo "Pushing Docker image..."

                    docker push "${DOCKER_IMAGE}:${IMAGE_TAG}"

                    echo ""
                    echo "=========================================="
                    echo " Docker image pushed successfully"
                    echo " Image: ${DOCKER_IMAGE}:${IMAGE_TAG}"
                    echo "=========================================="
                '''
            }
        }

        /*
         * ============================================================
         * 8. PIPELINE SUMMARY
         * ============================================================
         */
        stage('Pipeline Summary') {
            steps {

                echo '=========================================='
                echo '           PIPELINE SUMMARY'
                echo '=========================================='

                echo "Environment : ${params.ENVIRONMENT}"
                echo "Branch      : ${params.BRANCH}"
                echo "Image       : ${DOCKER_IMAGE}:${params.IMAGE_TAG}"
                echo "Push Image  : ${env.PUSH_IMAGE}"

                echo '=========================================='
            }
        }
    }

    /*
     * ================================================================
     * POST ACTIONS
     * ================================================================
     */
    post {

        success {

            echo '=========================================='
            echo '       PIPELINE SUCCESSFUL'
            echo '=========================================='

            echo "Build Number : ${env.BUILD_NUMBER}"
            echo "Environment  : ${params.ENVIRONMENT}"
            echo "Branch       : ${params.BRANCH}"
            echo "Docker Image : ${env.DOCKER_IMAGE}:${params.IMAGE_TAG}"

            echo '=========================================='
        }

        failure {

            echo '=========================================='
            echo '          PIPELINE FAILED'
            echo '=========================================='

            echo "Build Number : ${env.BUILD_NUMBER}"
            echo "Branch       : ${params.BRANCH}"

            echo '=========================================='
        }

        aborted {

            echo '=========================================='
            echo '         PIPELINE ABORTED'
            echo '=========================================='

            echo "Build Number : ${env.BUILD_NUMBER}"

            echo '=========================================='
        }

        always {

            echo '=========================================='
            echo '          CLEANING WORKSPACE'
            echo '=========================================='

            cleanWs(
                deleteDirs: true,
                disableDeferredWipeout: true,
                notFailBuild: true
            )

            echo 'Workspace cleanup completed'
        }
    }
}