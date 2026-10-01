pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                checkout scm
            }
        }

        stage('Environment Check') {
            steps {
                echo 'Checking Jenkins environment...'

                sh '''
                    echo "Java version:"
                    java -version

                    echo ""
                    echo "Maven version:"
                    mvn -version

                    echo ""
                    echo "Git version:"
                    git --version
                '''
            }
        }

        stage('Build') {
            steps {
                echo 'Building the application...'

                sh '''
                    mvn clean package -DskipTests
                '''
            }
        }

        stage('Test') {
            steps {
                echo 'Running tests...'

                sh '''
                    mvn test
                '''
            }
        }
    }

    post {
        success {
            echo '=========================================='
            echo ' Jenkins Pipeline SUCCESS '
            echo '=========================================='
        }

        failure {
            echo '=========================================='
            echo ' Jenkins Pipeline FAILED '
            echo '=========================================='
        }

        always {
            echo 'Pipeline execution completed.'
        }
    }
}