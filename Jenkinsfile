pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    parameters {

        choice(
            name: 'BRANCH',
            choices: [
                'feature/jenkins-argocd-cicd',
                'main',
                'develop'
            ],
            description: 'Select the Git branch to build'
        )

        choice(
            name: 'IMAGE_TAG',
            choices: [
                '1.0.0',
                '1.0.1',
                '1.0.2'
            ],
            description: 'Select the Docker image version/tag'
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

        booleanParam(
            name: 'RUN_TESTS',
            defaultValue: true,
            description: 'Run Maven tests'
        )

        booleanParam(
            name: 'PUSH_IMAGE',
            defaultValue: true,
            description: 'Push the Docker image to Docker Hub'
        )
    }

    environment {
        GITHUB_REPO = 'https://github.com/manjunath031984/Employment-Management.git'

        DOCKER_IMAGE = 'vannalmanju/employment-management'

        DOCKER_REGISTRY = 'docker.io'
    }

    stages {

        // =========================================================
        // 1. CHECKOUT GIT REPOSITORY
        // =========================================================

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
                            credentialsId: 'github-pat'
                        ]
                    ]
                ])

                sh '''
                    echo "Git checkout completed successfully"
                    echo ""
                    echo "Current branch:"
                    git branch --show-current
                    echo ""
                    echo "Latest commit:"
                    git log -1 --oneline
                '''
            }
        }


        // =========================================================
        // 2. MAVEN BUILD
        // =========================================================

        stage('Build Application') {
            steps {

                echo '=========================================='
                echo 'MAVEN BUILD'
                echo '=========================================='

                sh '''
                    echo "Java version:"
                    java -version

                    echo ""
                    echo "Maven version:"
                    mvn -version

                    echo ""
                    echo "Starting Maven build..."

                    mvn clean package -DskipTests

                    echo ""
                    echo "Maven build completed successfully"
                '''
            }
        }


        // =========================================================
        // 3. MAVEN TEST
        // =========================================================

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

                    mvn test

                    echo ""
                    echo "All Maven tests completed successfully"
                '''
            }
        }


        // =========================================================
        // 4. DOCKER BUILD
        // =========================================================

        stage('Docker Build') {
            steps {

                echo '=========================================='
                echo 'DOCKER BUILD'
                echo '=========================================='

                echo "Docker Image : ${env.DOCKER_IMAGE}"
                echo "Image Tag    : ${params.IMAGE_TAG}"

                sh '''
                    echo "Docker version:"
                    docker --version

                    echo ""
                    echo "Building Docker image..."

                    docker build \
                        -t ${DOCKER_IMAGE}:${IMAGE_TAG} \
                        .

                    echo ""
                    echo "Docker image built successfully"

                    echo ""
                    echo "Created image:"
                    docker images ${DOCKER_IMAGE}
                '''
            }
        }


        // =========================================================
        // 5. MANUAL APPROVAL
        // =========================================================

        stage('Input Approval') {

            when {
                expression {
                    return params.PUSH_IMAGE
                }
            }

            steps {

                echo '=========================================='
                echo 'WAITING FOR MANUAL APPROVAL'
                echo '=========================================='

                script {

                    def approval = input(
                        message: """
Do you want to push this Docker image to Docker Hub?

Repository:
${env.DOCKER_IMAGE}

Image Tag:
${params.IMAGE_TAG}

Environment:
${params.ENVIRONMENT}

Git Branch:
${params.BRANCH}
                        """,

                        ok: 'Approve & Push',

                        submitterParameter: 'APPROVED_BY'
                    )

                    echo "Deployment approved by: ${approval}"
                }
            }
        }


        // =========================================================
        // 6. PUSH TO DOCKER HUB
        // =========================================================

        stage('Push to Docker Hub') {

            when {
                expression {
                    return params.PUSH_IMAGE
                }
            }

            steps {

                echo '=========================================='
                echo 'PUSH IMAGE TO DOCKER HUB'
                echo '=========================================='

                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-pat',
                        usernameVariable: 'DOCKER_USERNAME',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )
                ]) {

                    sh '''
                        echo "Logging into Docker Hub..."

                        echo "$DOCKER_PASSWORD" | docker login \
                            --username "$DOCKER_USERNAME" \
                            --password-stdin

                        echo ""
                        echo "Docker login successful"

                        echo ""
                        echo "Pushing image..."

                        docker push ${DOCKER_IMAGE}:${IMAGE_TAG}

                        echo ""
                        echo "Docker image pushed successfully"

                        echo ""
                        echo "Image:"
                        echo "${DOCKER_IMAGE}:${IMAGE_TAG}"

                        echo ""
                        echo "Logging out from Docker Hub..."

                        docker logout
                    '''
                }
            }
        }
    }


    // =============================================================
    // POST ACTIONS
    // =============================================================

    post {

        success {

            echo '''
==========================================
PIPELINE SUCCESSFUL
==========================================
'''

            echo "Git Branch   : ${params.BRANCH}"
            echo "Environment  : ${params.ENVIRONMENT}"
            echo "Image        : ${DOCKER_IMAGE}:${params.IMAGE_TAG}"
            echo "Build Number : ${env.BUILD_NUMBER}"

            echo '''
==========================================
'''
        }

        failure {

            echo '''
==========================================
PIPELINE FAILED
==========================================
'''

            echo "Build Number : ${env.BUILD_NUMBER}"

            echo '''
==========================================
'''
        }

        aborted {

            echo '''
==========================================
PIPELINE ABORTED
==========================================
'''
        }

        always {

            echo "Pipeline execution completed."
        }
    }
}