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
            description: 'Select the Docker image version'
        )

        booleanParam(
            name: 'RUN_TESTS',
            defaultValue: true,
            description: 'Run Maven tests'
        )
    }

    environment {

        DOCKER_IMAGE = 'vannalmanju/employment-management'

        IMAGE_TAG = "${params.IMAGE_TAG}"

        GITHUB_CREDENTIALS = 'github-pat'

        DOCKERHUB_CREDENTIALS = 'dockerhub-pat'
    }

    stages {

        // =========================================================
        // 1. ENVIRONMENT CHECK
        // =========================================================

        stage('Environment Check') {

            steps {

                echo '''
==================================================
           ENVIRONMENT CHECK
==================================================
'''

                echo "Workspace    : ${WORKSPACE}"
                echo "Environment  : ${params.ENVIRONMENT}"
                echo "Git Branch   : ${params.BRANCH}"
                echo "Docker Image : ${DOCKER_IMAGE}"
                echo "Image Tag    : ${IMAGE_TAG}"
                echo "Run Tests    : ${params.RUN_TESTS}"

                sh '''
                    echo "Java:"
                    java -version

                    echo ""
                    echo "Maven:"
                    mvn -version

                    echo ""
                    echo "Docker:"
                    docker --version
                '''
            }
        }


        // =========================================================
        // 2. CHECKOUT GIT REPOSITORY
        // =========================================================

        stage('Checkout Git Repository') {

            steps {

                echo '''
==================================================
        CHECKOUT GIT REPOSITORY
==================================================
'''

                echo "Repository : https://github.com/manjunath031984/Employment-Management.git"
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
                            url: 'https://github.com/manjunath031984/Employment-Management.git',
                            credentialsId: "${GITHUB_CREDENTIALS}"
                        ]
                    ]
                ])

                sh '''
                    echo ""
                    echo "Repository checkout completed."

                    echo ""
                    echo "Workspace contents:"
                    ls -la

                    echo ""
                    echo "pom.xml:"
                    ls -lh pom.xml

                    echo ""
                    echo "Dockerfile:"
                    ls -lh Dockerfile
                '''
            }
        }


        // =========================================================
        // 3. MAVEN BUILD
        // =========================================================

        stage('Maven Build') {

            steps {

                echo '''
==================================================
              MAVEN BUILD
==================================================
'''

                sh '''
                    echo "Current directory:"
                    pwd

                    echo ""
                    echo "Checking pom.xml..."

                    if [ ! -f pom.xml ]; then
                        echo "ERROR: pom.xml not found."
                        exit 1
                    fi

                    echo "pom.xml found."

                    echo ""
                    echo "Starting Maven build..."

                    mvn clean package -DskipTests

                    echo ""
                    echo "Maven build completed successfully."

                    echo ""
                    echo "Generated artifacts:"
                    ls -lh target/ || true
                '''
            }
        }


        // =========================================================
        // 4. MAVEN TEST
        // =========================================================

        stage('Maven Test') {

            when {

                expression {
                    return params.RUN_TESTS
                }
            }

            steps {

                echo '''
==================================================
               MAVEN TEST
==================================================
'''

                sh '''
                    echo "Running Maven tests..."

                    mvn test

                    echo ""
                    echo "Maven tests completed successfully."
                '''
            }
        }


        // =========================================================
        // 5. DOCKER BUILD
        // =========================================================

        stage('Docker Build') {

            steps {

                echo '''
==================================================
                DOCKER BUILD
==================================================
'''

                echo "Docker Image : ${DOCKER_IMAGE}"
                echo "Image Tag    : ${IMAGE_TAG}"
                echo "Build Context: ${WORKSPACE}"

                sh '''
                    echo "Current directory:"
                    pwd

                    echo ""
                    echo "Dockerfile:"
                    ls -lh Dockerfile

                    echo ""
                    echo "Docker version:"
                    docker --version

                    echo ""
                    echo "Building Docker image..."

                    docker build \
                        -t "${DOCKER_IMAGE}:${IMAGE_TAG}" \
                        .

                    echo ""
                    echo "Docker image built successfully."

                    echo ""
                    echo "Created image:"

                    docker images "${DOCKER_IMAGE}" \
                        --format "table {{.Repository}}\\t{{.Tag}}\\t{{.ID}}\\t{{.Size}}"
                '''
            }
        }


        // =========================================================
        // 6. DOCKER HUB INPUT REQUEST
        // =========================================================

        stage('Docker Hub Input Request') {

            steps {

                script {

                    def pushImage = input(
                        message: """
Do you want to push this Docker image to Docker Hub?

Environment : ${params.ENVIRONMENT}
Branch      : ${params.BRANCH}
Image       : ${DOCKER_IMAGE}
Tag         : ${IMAGE_TAG}

Docker Hub Repository:
vannalmanju/employment-management
""",

                        ok: 'Submit',

                        parameters: [
                            choice(
                                name: 'PUSH_IMAGE',
                                choices: [
                                    'YES',
                                    'NO'
                                ],
                                description: 'Select YES to push the Docker image'
                            )
                        ]
                    )

                    echo "Docker Hub Push Selection: ${pushImage}"

                    if (pushImage == 'YES') {

                        env.PUSH_IMAGE = 'true'

                        echo "Docker image will be pushed."

                    } else {

                        env.PUSH_IMAGE = 'false'

                        echo "Docker image will NOT be pushed."
                    }
                }
            }
        }


        // =========================================================
        // 7. DOCKER HUB LOGIN
        // =========================================================

        stage('Docker Hub Login') {

            when {

                expression {
                    return env.PUSH_IMAGE == 'true'
                }
            }

            steps {

                echo '''
==================================================
             DOCKER HUB LOGIN
==================================================
'''

                withCredentials([
                    usernamePassword(
                        credentialsId: "${DOCKERHUB_CREDENTIALS}",
                        usernameVariable: 'DOCKER_USERNAME',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )
                ]) {

                    sh '''
                        echo "Logging in to Docker Hub..."

                        echo "${DOCKER_PASSWORD}" | docker login \
                            --username "${DOCKER_USERNAME}" \
                            --password-stdin

                        echo ""
                        echo "Docker Hub login successful."
                    '''
                }
            }
        }


        // =========================================================
        // 8. PUSH TO DOCKER HUB
        // =========================================================

        stage('Push to Docker Hub') {

            when {

                expression {
                    return env.PUSH_IMAGE == 'true'
                }
            }

            steps {

                echo '''
==================================================
            PUSH TO DOCKER HUB
==================================================
'''

                sh '''
                    echo "Docker image:"
                    echo "${DOCKER_IMAGE}:${IMAGE_TAG}"

                    echo ""
                    echo "Pushing Docker image..."

                    docker push "${DOCKER_IMAGE}:${IMAGE_TAG}"

                    echo ""
                    echo "=========================================="
                    echo " Docker image pushed successfully"
                    echo "=========================================="

                    echo ""
                    echo "Docker Hub Image:"
                    echo "${DOCKER_IMAGE}:${IMAGE_TAG}"
                '''
            }
        }


        // =========================================================
        // 9. PIPELINE SUMMARY
        // =========================================================

        stage('Pipeline Summary') {

            steps {

                echo '''
==================================================
             PIPELINE SUMMARY
==================================================
'''

                echo "Application  : Employee Management"
                echo "Environment  : ${params.ENVIRONMENT}"
                echo "Branch       : ${params.BRANCH}"
                echo "Workspace    : ${WORKSPACE}"
                echo "Docker Image : ${DOCKER_IMAGE}"
                echo "Image Tag    : ${IMAGE_TAG}"
                echo "Docker Push  : ${env.PUSH_IMAGE ?: 'false'}"
                echo "Build Number : ${BUILD_NUMBER}"
                echo "Build URL    : ${BUILD_URL}"

                echo '''
==================================================
          PIPELINE EXECUTION COMPLETED
==================================================
'''
            }
        }
    }


    // =============================================================
    // POST ACTIONS
    // =============================================================

    post {

        success {

            echo '''
==================================================
              PIPELINE SUCCESS
==================================================
'''

            echo "Build Number : ${BUILD_NUMBER}"
            echo "Environment  : ${params.ENVIRONMENT}"
            echo "Branch       : ${params.BRANCH}"
            echo "Image        : ${DOCKER_IMAGE}:${IMAGE_TAG}"

            echo '''
==================================================
'''
        }

        failure {

            echo '''
==================================================
               PIPELINE FAILED
==================================================
'''

            echo "Build Number : ${BUILD_NUMBER}"
            echo "Branch       : ${params.BRANCH}"

            echo '''
Please check the Jenkins console output.
==================================================
'''
        }

        aborted {

            echo '''
==================================================
             PIPELINE ABORTED
==================================================
'''

            echo "Build Number : ${BUILD_NUMBER}"
        }

        always {

            echo '''
==================================================
              CLEANING WORKSPACE
==================================================
'''

            cleanWs(
                deleteDirs: true,
                disableDeferredWipeout: true,
                notFailBuild: true
            )

            echo "Workspace cleanup completed."
        }
    }
}