pipeline {
    agent any

    environment {
        GIT_CREDENTIALS = 'argocd-id'                        // Jenkins credential for GitOps repo
        TARGET_REPO = 'https://github.com/muthuraj-rajarathinam/Argocd-connector-saas.git'
        IMAGE_NAME = "muthuraj07/gitapp"                       // Docker image name
        DOCKER_CREDENTIALS = 'docker-hub-id'                 // Jenkins Docker Hub credentials
        IMAGE_TAG = "${env.BUILD_NUMBER}"                    // Unique tag per build
        DEPLOYMENT_FILE = "dev/app-deployment.yaml"         // Path inside GitOps repo
    }

    stages {
        stage('Checkout GitOps Repo') {
            steps {
                git branch: 'main',
                    credentialsId: "${env.GIT_CREDENTIALS}",
                    url: "${env.TARGET_REPO}"
            }
        }

        stage('Build & Push Docker Image') {
            steps {
                script {
                    sh """
                        # Build Docker image with unique tag
                        docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
                        
                        # Login to Docker Hub
                        echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin
                        docker push ${IMAGE_NAME}:${IMAGE_TAG}
                    """
                }
            }
        }

        stage('Update GitOps Deployment') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: "${env.GIT_CREDENTIALS}", 
                    usernameVariable: 'GITHUB_USERNAME', 
                    passwordVariable: 'GITHUB_TOKEN')]) {
                    sh """
                        # Navigate to dev folder where deployment YAML is
                        cd dev
                        
                        # Update image tag in deployment YAML
                        sed -i "s|image: .*|image: ${IMAGE_NAME}:${IMAGE_TAG}|g" app-deployment.yaml
                        
                        # Configure git
                        git config user.email "jenkins@example.com"
                        git config user.name "Jenkins CI"

                        # Commit & push changes
                        git add app-deployment.yaml
                        git commit -m "Update image to ${IMAGE_NAME}:${IMAGE_TAG}" || echo "No changes to commit"
                        git push https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@github.com/muthuraj-rajarathinam/Argocd-connector-saas.git main
                    """
                }
            }
        }
    }

    post {
        success {
            echo "✅ Docker image built and GitOps repo updated. Argo CD will deploy automatically!"
        }
        failure {
            echo "❌ Pipeline failed. Check logs."
        }
    }
}

