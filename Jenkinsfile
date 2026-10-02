pipeline {

    agent any

    environment {
        IMAGE_NAME = 'vannalmanju/employment-management'
        DOCKER_REGISTRY = 'docker.io'
    }

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
            description: 'Select the Docker image version'
        )

        booleanParam(
            name: 'RUN_TESTS',
            defaultValue: true,
            description: 'Run Maven tests'
        )

        booleanParam(
            name: 'PUSH_TO_DOCKERHUB',
            defaultValue: true,
            description: 'Request approval to push the Docker image to Docker Hub'
        )
    }

    stages {

        /*
         * ============================================================
         * ENVIRONMENT CHECK
         * ============================================================
         */

        stage('Environment Check') {
            steps {

                echo '''
========================================================
           EMPLOYMENT MANAGEMENT CI/CD
========================================================
'''

                echo "Environment       : ${params.ENVIRONMENT}"
                echo "Git Branch        : ${params.BRANCH}"
                echo "Docker Image      : ${IMAGE_NAME}"
                echo "Image Tag         : ${params.IMAGE_TAG}"
                echo "Run Tests         : ${params.RUN_TESTS}"
                echo "Push to DockerHub : ${params.PUSH_TO_DOCKERHUB}"

                echo '''
========================================================
'''
            }
        }


        /*
         * ============================================================
         * CHECKOUT GIT REPOSITORY
         * ============================================================
         */

        stage('Checkout Git Repository') {
            steps {

                echo '========================================================'
                echo 'CHECKOUT GIT REPOSITORY'
                echo '========================================================'

                echo "Checking out branch: ${params.BRANCH}"

                checkout([
                    $class: 'GitSCM',

                    branches: [
                        [
                            name: "*/${params.BRANCH}"
                        ]
                    ],

                    userRemoteConfigs: [
                        [
                            url: 'https://github.com/manjunath031984/Employment-Management.git',
                            credentialsId: 'github-pat'
                        ]
                    ]
                ])

                sh '''
                    echo "Current Git branch:"
                    git branch --show-current

                    echo ""
                    echo "Latest commit:"
                    git log -1 --oneline
                '''
            }
        }


        /*
         * ============================================================
         * MAVEN BUILD
         * ============================================================
         */

        stage('Maven Build') {
            steps {

                echo '========================================================'
                echo 'MAVEN BUILD'
                echo '========================================================'

                sh '''
                    echo "Maven version:"
                    mvn --version

                    echo ""
                    echo "Building Spring Boot application..."

                    mvn clean package -DskipTests

                    echo ""
                    echo "Maven build completed successfully."
                '''
            }
        }


        /*
         * ============================================================
         * MAVEN TEST
         * ============================================================
         */

        stage('Maven Test') {

            when {
                expression {
                    return params.RUN_TESTS
                }
            }

            steps {

                echo '========================================================'
                echo 'MAVEN TEST'
                echo '========================================================'

                sh '''
                    echo "Running Maven tests..."

                    mvn test

                    echo ""
                    echo "All Maven tests completed successfully."
                '''
            }
        }


        /*
         * ============================================================
         * DOCKER BUILD
         * ============================================================
         */

        stage('Docker Build') {
            steps {

                echo '========================================================'
                echo 'DOCKER BUILD'
                echo '========================================================'

                echo "Docker Image : ${IMAGE_NAME}"
                echo "Image Tag    : ${params.IMAGE_TAG}"

                sh """
                    echo "Docker version:"
                    docker --version

                    echo ""
                    echo "Building Docker image..."

                    docker build \
                        -t ${IMAGE_NAME}:${params.IMAGE_TAG} \
                        .

                    echo ""
                    echo "Docker image built successfully."

                    echo ""
                    echo "Docker image:"
                    docker images ${IMAGE_NAME}
                """
            }
        }


        /*
         * ============================================================
         * DOCKER IMAGE INPUT REQUEST
         * ============================================================
         */

        stage('Docker Hub Input Request') {

            when {
                expression {
                    return params.PUSH_TO_DOCKERHUB
                }
            }

            steps {

                script {

                    def approval = input(
                        id: 'DockerHubApproval',
                        message: """Docker Hub Push Approval

Docker Image : ${IMAGE_NAME}
Image Tag    : ${params.IMAGE_TAG}
Environment  : ${params.ENVIRONMENT}
Git Branch   : ${params.BRANCH}

Do you want to push this image to Docker Hub?""",

                        ok: 'Submit',

                        parameters: [
                            choice(
                                name: 'PUSH_IMAGE',
                                choices: [
                                    'YES',
                                    'NO'
                                ],
                                description: 'Select YES to push the Docker image to Docker Hub'
                            )
                        ]
                    )

                    echo "Docker Hub approval response: ${approval}"

                    if (approval == 'NO') {

                        error(
                            "Docker Hub push was rejected by the user."
                        )
                    }

                    echo "Docker Hub push approved."
                }
            }
        }


        /*
         * ============================================================
         * DOCKER HUB LOGIN
         * ============================================================
         */

        stage('Docker Hub Login') {

            when {
                expression {
                    return params.PUSH_TO_DOCKERHUB
                }
            }

            steps {

                echo '========================================================'
                echo 'DOCKER HUB LOGIN'
                echo '========================================================'

                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKER_USERNAME',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )
                ]) {

                    sh '''
                        echo "Logging in to Docker Hub..."

                        echo "$DOCKER_PASSWORD" | docker login \
                            --username "$DOCKER_USERNAME" \
                            --password-stdin

                        echo ""
                        echo "Docker Hub login successful."
                    '''
                }
            }
        }


        /*
         * ============================================================
         * PUSH TO DOCKER HUB
         * ============================================================
         */

        stage('Push to Docker Hub') {

            when {
                expression {
                    return params.PUSH_TO_DOCKERHUB
                }
            }

            steps {

                echo '========================================================'
                echo 'PUSH TO DOCKER HUB'
                echo '========================================================'

                echo "Pushing:"
                echo "${IMAGE_NAME}:${params.IMAGE_TAG}"

                sh """
                    docker push ${IMAGE_NAME}:${params.IMAGE_TAG}
                """

                echo '========================================================'
                echo 'DOCKER IMAGE PUSH SUCCESSFUL'
                echo '========================================================'

                echo "Docker Hub Image:"
                echo "${IMAGE_NAME}:${params.IMAGE_TAG}"
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

            echo '''
========================================================
             PIPELINE SUCCESSFUL
========================================================
'''

            echo "Environment : ${params.ENVIRONMENT}"
            echo "Branch      : ${params.BRANCH}"
            echo "Image       : ${IMAGE_NAME}:${params.IMAGE_TAG}"

            echo '''
========================================================
'''
        }

        failure {

            echo '''
========================================================
               PIPELINE FAILED
========================================================
'''

            echo "Build Number: ${env.BUILD_NUMBER}"

            echo '''
========================================================
'''
        }

        aborted {

            echo '''
========================================================
             PIPELINE ABORTED
========================================================
'''
        }

        always {

            echo "Pipeline execution completed."
            echo "Build Number: ${env.BUILD_NUMBER}"
        }
    }
}