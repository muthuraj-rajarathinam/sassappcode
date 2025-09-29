pipeline {
    agent any

    environment {
        GIT_CREDENTIALS = 'argocd-id'                        
        TARGET_REPO = 'https://github.com/muthuraj-rajarathinam/Argocd-connector-saas.git'
        IMAGE_NAME = "muthuraj07/gitapp"        // Docker Hub repo
        DOCKER_CREDENTIALS = 'dockerhub-creds'  // Make sure this matches Jenkins credential ID
        IMAGE_TAG = "${env.BUILD_NUMBER}"       // Unique tag per build
        DEPLOYMENT_FILE = "dev/app-deployment.yaml"
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
                withCredentials([usernamePassword(
                    credentialsId: "${env.DOCKER_CREDENTIALS}", 
                    usernameVariable: 'DOCKER_USERNAME', 
                    passwordVariable: 'DOCKER_PASSWORD')]) {
                    
                    sh """
                        echo "${DOCKER_PASSWORD}" | docker login -u "${DOCKER_USERNAME}" --password-stdin
                        docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
                        docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest
                        docker push ${IMAGE_NAME}:${IMAGE_TAG}
                        docker push ${IMAGE_NAME}:latest
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
                        cd dev
                        sed -i "s|image: .*|image: ${IMAGE_NAME}:${IMAGE_TAG}|g" app-deployment.yaml
                        
                        git config user.email "jenkins@example.com"
                        git config user.name "Jenkins CI"

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
            echo "✅ Docker image built, pushed, and GitOps repo updated. Argo CD will deploy automatically!"
        }
        failure {
            echo "❌ Pipeline failed. Check logs."
        }
    }
}

