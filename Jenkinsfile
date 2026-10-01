pipeline {
    agent any

    stages {
        stage('Webhook Test') {
            steps {
                echo 'GitHub webhook triggered Jenkins successfully!'
                echo "Build Number: ${env.BUILD_NUMBER}"
                echo "Branch: ${env.BRANCH_NAME}"
            }
        }
    }
}