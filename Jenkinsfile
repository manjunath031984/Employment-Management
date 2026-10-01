pipeline {
    agent any

    parameters {
        choice(
            name: 'ENVIRONMENT',
            choices: ['dev', 'staging', 'prod'],
            description: 'Select the deployment environment'
        )

        choice(
            name: 'ACTION',
            choices: ['build', 'test', 'deploy'],
            description: 'Select the pipeline action'
        )

        string(
            name: 'BRANCH',
            defaultValue: 'feature/jenkins-argocd-cicd',
            description: 'Git branch to build'
        )

        booleanParam(
            name: 'RUN_TESTS',
            defaultValue: true,
            description: 'Run application tests'
        )

        booleanParam(
            name: 'DEPLOY',
            defaultValue: false,
            description: 'Deploy the application'
        )
    }

    stages {

        stage('Environment Check') {
            steps {
                echo "======================================"
                echo "Environment : ${params.ENVIRONMENT}"
                echo "Action      : ${params.ACTION}"
                echo "Branch      : ${params.BRANCH}"
                echo "Run Tests   : ${params.RUN_TESTS}"
                echo "Deploy      : ${params.DEPLOY}"
                echo "======================================"
            }
        }

        stage('Checkout') {
            steps {
                echo "Checking out branch: ${params.BRANCH}"

                checkout([
                    $class: 'GitSCM',
                    branches: [[name: "*/${params.BRANCH}"]],
                    userRemoteConfigs: [[
                        url: 'https://github.com/manjunath031984/Employment-Management.git',
                        credentialsId: 'github-pat'
                    ]]
                ])
            }
        }

        stage('Build') {
            when {
                expression {
                    params.ACTION in ['build', 'test', 'deploy']
                }
            }

            steps {
                echo "Building application..."
                sh '''
                    echo "Build started"
                    echo "Build completed successfully"
                '''
            }
        }

        stage('Test') {
            when {
                expression {
                    params.RUN_TESTS &&
                    params.ACTION in ['test', 'deploy']
                }
            }

            steps {
                echo "Running tests..."

                sh '''
                    echo "Tests started"
                    echo "All tests passed successfully"
                '''
            }
        }

        stage('Deploy') {
            when {
                expression {
                    params.DEPLOY &&
                    params.ACTION == 'deploy'
                }
            }

            steps {
                echo "Deploying application to ${params.ENVIRONMENT}..."

                sh '''
                    echo "Deployment started"
                    echo "Deployment completed successfully"
                '''
            }
        }

        stage('Webhook Test') {
            steps {
                echo "GitHub webhook / Jenkins build test successful!"
                echo "Build Number: ${env.BUILD_NUMBER}"
                echo "Triggered by branch: ${params.BRANCH}"
            }
        }
    }

    post {
        success {
            echo "======================================"
            echo "PIPELINE SUCCESSFUL"
            echo "Environment: ${params.ENVIRONMENT}"
            echo "Build: ${env.BUILD_NUMBER}"
            echo "======================================"
        }

        failure {
            echo "======================================"
            echo "PIPELINE FAILED"
            echo "Build: ${env.BUILD_NUMBER}"
            echo "======================================"
        }

        always {
            echo "Pipeline execution completed."
        }
    }
}