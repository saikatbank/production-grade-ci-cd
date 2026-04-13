pipeline {
    agent any

    parameters {
        string(
            name: 'ROLLBACK_VERSION',
            defaultValue: '',
            description: 'Leave empty for a normal build. Enter a version (e.g. 1.2.0) to rollback to that version on EC2.'
        )
    }

    environment {
        // Docker Hub registry details
        DOCKER_REGISTRY = 'docker.io'
        DOCKER_NAMESPACE = 'saikatbank'
        IMAGE_NAME = 'fastapi-app'

        // Jenkins Credentials IDs
        REGISTRY_CREDENTIALS_ID = 'docker-registry-creds'
        GITHUB_CREDENTIALS_ID = 'github-token' // Replace with your Jenkins credential ID for GitHub PAT

        // EC2 Deployment Variables
        EC2_IP = '54.175.5.180'
        EC2_CREDENTIALS_ID = 'app-server-cred'
    }

    stages {

        // ──────────────────────────────────────────────
        //  ROLLBACK MODE — Skip straight to deployment
        // ──────────────────────────────────────────────
        stage('Rollback Setup') {
            when {
                expression { return params.ROLLBACK_VERSION?.trim() }
            }
            steps {
                script {
                    echo "🔁 ROLLBACK MODE — Rolling back to version ${params.ROLLBACK_VERSION}"
                    env.IMAGE_TAG = params.ROLLBACK_VERSION.trim()
                    env.FULL_IMAGE_NAME = "${env.DOCKER_REGISTRY}/${env.DOCKER_NAMESPACE}/${env.IMAGE_NAME}:${env.IMAGE_TAG}"
                }
            }
        }

        // ──────────────────────────────────────────────
        //  NORMAL BUILD FLOW (skipped during rollback)
        // ──────────────────────────────────────────────
        stage('Checkout') {
            when {
                expression { return !params.ROLLBACK_VERSION?.trim() }
            }
            steps {
                checkout scm
            }
        }

        stage('Lint & Format') {
            when {
                expression { return !params.ROLLBACK_VERSION?.trim() }
            }
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
            when {
                expression { return !params.ROLLBACK_VERSION?.trim() }
            }
            agent {
                docker {
                    image 'python:3.11-slim'
                    args '-u root:root'
                }
            }
            environment {
                POSTGRES_SERVER = 'localhost'
                POSTGRES_USER = 'test_user'
                POSTGRES_PASSWORD = 'test_password'
                POSTGRES_DB = 'test_db'
            }
            steps {
                echo "Running Unit Tests..."
                sh '''
                    . venv/bin/activate
                    # Run tests and output JUnit XML report
                    pip install -r requirements-dev.txt
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

        // ──────────────────────────────────────────────
        //  VERSION BUMP — Only after quality gates pass
        // ──────────────────────────────────────────────
        stage('Version Bump') {
            when {
                expression { return !params.ROLLBACK_VERSION?.trim() }
            }
            steps {
                script {
                    // Fetch all existing tags from origin
                    sh 'git fetch --tags'

                    // Check if the current commit (HEAD) already has a version tag
                    def existingTag = sh(
                        script: "git tag -l 'v*.*.*' --points-at HEAD | head -1",
                        returnStdout: true
                    ).trim()

                    if (existingTag) {
                        // This commit was already tagged — reuse the existing version
                        def existingVersion = existingTag.replaceFirst('v', '')
                        echo "⏭️ HEAD is already tagged as ${existingTag}. Skipping version bump."

                        env.IMAGE_TAG = existingVersion
                        env.FULL_IMAGE_NAME = "${env.DOCKER_REGISTRY}/${env.DOCKER_NAMESPACE}/${env.IMAGE_NAME}:${existingVersion}"
                        return
                    }

                    // Find the latest semantic version tag (e.g. v1.2.3)
                    def latestTag = sh(
                        script: "git tag -l 'v*.*.*' --sort=-v:refname | head -1",
                        returnStdout: true
                    ).trim()

                    if (!latestTag) {
                        latestTag = 'v0.0.0'
                        echo "No existing version tags found. Starting from v0.0.0"
                    }

                    echo "Latest tag: ${latestTag}"

                    // Parse the current version components
                    def version = latestTag.replaceFirst('v', '')
                    def parts = version.split('\\.')
                    def major = parts[0].toInteger()
                    def minor = parts[1].toInteger()
                    def patch = parts[2].toInteger()

                    // Read the latest commit message to determine the bump type
                    def commitMsg = sh(
                        script: 'git log -1 --pretty=%B',
                        returnStdout: true
                    ).trim()

                    echo "Last commit: ${commitMsg}"

                    // Determine bump type based on Conventional Commits
                    def bumpType = 'patch' // safe default

                    if (commitMsg.contains('BREAKING CHANGE') || commitMsg =~ /^\w+!:/) {
                        bumpType = 'major'
                        major++; minor = 0; patch = 0
                    } else if (commitMsg.startsWith('feat:') || commitMsg.startsWith('feat(')) {
                        bumpType = 'minor'
                        minor++; patch = 0
                    } else {
                        patch++
                    }

                    def newVersion = "${major}.${minor}.${patch}"

                    echo "📦 Version bump: ${latestTag} → v${newVersion} (${bumpType})"

                    // Set environment variables for downstream stages
                    env.IMAGE_TAG = newVersion
                    env.FULL_IMAGE_NAME = "${env.DOCKER_REGISTRY}/${env.DOCKER_NAMESPACE}/${env.IMAGE_NAME}:${newVersion}"

                    // Configure Git identity for the tag commit
                    sh 'git config user.email "jenkins@ci.local"'
                    sh 'git config user.name "Jenkins CI"'

                    // Create an annotated tag
                    sh "git tag -a v${newVersion} -m 'Release v${newVersion} [${bumpType}]'"

                    // Push the tag back to GitHub using PAT (stored as "Secret text" credential)
                    // Note: Even public repos require authentication for write operations (push)
                    withCredentials([string(credentialsId: env.GITHUB_CREDENTIALS_ID, variable: 'GIT_TOKEN')]) {
                        sh 'git push https://x-access-token:${GIT_TOKEN}@github.com/saikatbank/production-grade-ci-cd.git v' + newVersion
                    }

                    echo "✅ Tagged and pushed v${newVersion} to GitHub"
                }
            }
        }

        stage('Docker Build') {
            when {
                expression { return !params.ROLLBACK_VERSION?.trim() }
            }
            steps {
                echo "Building Docker image: ${FULL_IMAGE_NAME}"
                sh "docker build -t ${FULL_IMAGE_NAME} ."
                sh "docker tag ${FULL_IMAGE_NAME} ${DOCKER_REGISTRY}/${DOCKER_NAMESPACE}/${IMAGE_NAME}:latest"
            }
        }

        stage('Docker Push') {
            when {
                expression { return !params.ROLLBACK_VERSION?.trim() }
            }
            steps {
                echo "Pushing Docker image to the registry..."
                withCredentials([usernamePassword(credentialsId: env.REGISTRY_CREDENTIALS_ID, passwordVariable: 'DOCKER_PASS', usernameVariable: 'DOCKER_USER')]) {
                    sh 'echo "$DOCKER_PASS" | docker login "$DOCKER_REGISTRY" -u "$DOCKER_USER" --password-stdin'
                    sh 'docker push "$FULL_IMAGE_NAME"'
                    sh 'docker push "$DOCKER_REGISTRY/$DOCKER_NAMESPACE/$IMAGE_NAME:latest"'
                    sh 'docker logout "$DOCKER_REGISTRY"'
                }
            }
        }

        // ──────────────────────────────────────────────
        //  DEPLOY (runs for both normal build & rollback)
        // ──────────────────────────────────────────────
        stage('Deploy to EC2') {
            steps {
                echo "🚀 Deploying ${FULL_IMAGE_NAME} to EC2 at ${EC2_IP}..."

                withCredentials([sshUserPrivateKey(credentialsId: env.EC2_CREDENTIALS_ID, keyFileVariable: 'SSH_KEY', usernameVariable: 'EC2_USER')]) {

                    // Step 1: Save the currently running image tag as a rollback breadcrumb
                    sh '''
                        ssh -i $SSH_KEY -o StrictHostKeyChecking=no $EC2_USER@$EC2_IP \
                            "cd app 2>/dev/null && docker compose ps -q web 2>/dev/null && \
                             docker inspect --format='{{.Config.Image}}' fastapi_web_prod 2>/dev/null > app/.previous_image || echo 'No previous deployment found'"
                    '''

                    // Step 2: Ensure the app directory exists
                    sh 'ssh -i $SSH_KEY -o StrictHostKeyChecking=no $EC2_USER@$EC2_IP "mkdir -p app && touch app/.env"'

                    // Step 3: Copy the production docker-compose file
                    sh 'scp -i $SSH_KEY -o StrictHostKeyChecking=no docker-compose.prod.yml $EC2_USER@$EC2_IP:app/docker-compose.yml'

                    // Step 4: Pull the new image and deploy
                    sh 'ssh -i $SSH_KEY -o StrictHostKeyChecking=no $EC2_USER@$EC2_IP "cd app && export APP_IMAGE=$FULL_IMAGE_NAME && docker compose pull && docker compose up -d"'

                    // Step 5: Health check — wait for the app to become healthy
                    script {
                        def healthy = false
                        def maxRetries = 6
                        def waitSeconds = 10

                        for (int i = 1; i <= maxRetries; i++) {
                            echo "Health check attempt ${i}/${maxRetries}..."
                            sleep(waitSeconds)

                            def status = sh(
                                script: "ssh -i \$SSH_KEY -o StrictHostKeyChecking=no \$EC2_USER@\$EC2_IP 'curl -sf http://localhost/health/live'",
                                returnStatus: true
                            )

                            if (status == 0) {
                                healthy = true
                                echo "✅ Health check passed on attempt ${i}"
                                break
                            }
                            echo "⏳ Health check failed, retrying in ${waitSeconds}s..."
                        }

                        // Step 6: Auto-rollback if health check failed
                        if (!healthy) {
                            echo "❌ Health check failed after ${maxRetries} attempts. Initiating auto-rollback..."

                            def prevImage = sh(
                                script: "ssh -i \$SSH_KEY -o StrictHostKeyChecking=no \$EC2_USER@\$EC2_IP 'cat app/.previous_image 2>/dev/null'",
                                returnStdout: true
                            ).trim()

                            if (prevImage && prevImage != 'No previous deployment found') {
                                echo "🔁 Rolling back to previous image: ${prevImage}"
                                sh "ssh -i \$SSH_KEY -o StrictHostKeyChecking=no \$EC2_USER@\$EC2_IP 'cd app && export APP_IMAGE=${prevImage} && docker compose pull && docker compose up -d'"
                                error("Deployment failed health check. Auto-rolled back to ${prevImage}. Build marked as FAILED.")
                            } else {
                                error("Deployment failed health check and no previous image found to rollback to. Manual intervention required!")
                            }
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            // Clean up the Docker image locally to save space on the Jenkins worker
            sh "docker rmi ${FULL_IMAGE_NAME} || true"
            sh "docker rmi ${DOCKER_REGISTRY}/${DOCKER_NAMESPACE}/${IMAGE_NAME}:latest || true"

            // Clean up the workspace to prevent residue for next builds
            cleanWs()
        }
        success {
            echo "✅ Pipeline completed successfully! Version: ${env.IMAGE_TAG}"
        }
        failure {
            echo "❌ Pipeline failed! Please check Jenkins console logs."
        }
    }
}
