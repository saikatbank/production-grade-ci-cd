pipeline {
    agent any

    environment {
        // Define repository/image details here
        // As we are using docker hub, so kept DOCKER_REGISTRY=docker.io
        DOCKER_REGISTRY = 'docker.io' // Replace with your actual registry URL (e.g., xxx.dkr.ecr.region.amazonaws.com)
        IMAGE_NAME = 'fastapi-app'
        IMAGE_TAG = "${env.BUILD_NUMBER}"
        FULL_IMAGE_NAME = "${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"

        // Uncomment and replace with your Jenkins credentials ID for the registry
        REGISTRY_CREDENTIALS_ID = 'docker-registry-creds'
    }

    stages {
        stage('Checkout') {
            steps {
                // Checkout source code from SCM (Git)
                checkout scm
            }
        }

        stage('Lint & Format') {
            agent {
                docker {
                    image 'python:3.11-slim'
                    args '-u root:root'
                }
            }
            steps {
                echo "Running Code Linting and Formatting..."
                sh '''
                    # Setup virtual environment and install dev dependencies
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install black ruff

                    # Run the linting script which executes black and ruff
                    bash scripts/lint.sh
                '''
            }
        }

        stage('Unit Tests') {
            agent {
                docker {
                    image 'python:3.11-slim'
                    args '-u root:root'
                }
            }
            steps {
                echo "Running Unit Tests..."
                sh '''
                    . venv/bin/activate
                    # Run tests and output JUnit XML report
                    pip install pytest
                    pytest tests/ -v --junitxml=test-results.xml
                '''
            }
            post {
                always {
                    // Archive the test results regardless of build success or failure
                    junit 'test-results.xml'
                }
            }
        }

        stage('Docker Build') {
            steps {
                echo "Building Docker image: ${FULL_IMAGE_NAME}"
                sh "docker build -t ${FULL_IMAGE_NAME} ."
                // Best practice: tag it as 'latest' as well locally in the build
                sh "docker tag ${FULL_IMAGE_NAME} ${DOCKER_REGISTRY}/${IMAGE_NAME}:latest"
            }
        }

        stage('Docker Push') {
            steps {
                echo "Pushing Docker image to the registry..."

                /*
                 * In a real production setup, you would authenticate to your registry using Jenkins credentials.
                 * Uncomment and adapt the snippet below based on your registry type.
                 */

                withCredentials([usernamePassword(credentialsId: env.REGISTRY_CREDENTIALS_ID, passwordVariable: 'DOCKER_PASS', usernameVariable: 'DOCKER_USER')]) {
                    sh "echo $DOCKER_PASS | docker login ${DOCKER_REGISTRY} -u $DOCKER_USER --password-stdin"
                    sh "docker push ${FULL_IMAGE_NAME}"
                    sh "docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}:latest"
                    sh "docker logout ${DOCKER_REGISTRY}"
                }

                // Placeholder since we are skipping the actual push without real credentials
                sh "echo 'Pretending to push ${FULL_IMAGE_NAME} to ${DOCKER_REGISTRY}...'"
            }
        }
    }

    post {
        always {
            // Clean up the Docker image locally to save space on the Jenkins worker
            sh "docker rmi ${FULL_IMAGE_NAME} || true"
            sh "docker rmi ${DOCKER_REGISTRY}/${IMAGE_NAME}:latest || true"

            // Clean up the workspace to prevent residue for next builds
            cleanWs()
        }
        success {
            echo "Pipeline completed successfully!"
            // Here you could send a Slack/Email notification on success
        }
        failure {
            echo "Pipeline failed! Please check Jenkins console logs."
            // Here you could send a Slack/Email notification on failure
        }
    }
}
