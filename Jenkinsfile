pipeline {
    agent any

    environment {
        APP_REPO_CREDENTIALS = 'sass-code'                        
        APP_REPO = 'https://github.com/muthuraj-rajarathinam/sassappcode.git'
        GITOPS_REPO_CREDENTIALS = 'argocd-id'                        
        GITOPS_REPO = 'https://github.com/muthuraj-rajarathinam/Argocd-connector-saas.git'
        IMAGE_NAME = "muthuraj07/gitapp"        // Docker Hub repo
        DOCKER_CREDENTIALS = 'dockerhub-creds'  // Jenkins Docker Hub creds
        IMAGE_TAG = "${env.BUILD_NUMBER}"       // Unique tag per build
        DEPLOYMENT_FILE = "dev/app-deployment.yaml"
    }

    stages {
        stage('Checkout App Repo') {
            steps {
                git branch: 'main',
                    credentialsId: "${env.APP_REPO_CREDENTIALS}",
                    url: "${env.APP_REPO}"
            }
        }

        stage('Build & Push Docker Image') {
            steps {
                sh 'ls -l'  // debug: confirm Dockerfile exists here
                withDockerRegistry([credentialsId: "${env.DOCKER_CREDENTIALS}", url: '']) {
                    sh """
                        docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
                        docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest
                        docker push ${IMAGE_NAME}:${IMAGE_TAG}
                        docker push ${IMAGE_NAME}:latest
                    """
                }
            }
        }

        stage('Checkout GitOps Repo') {
            steps {
                git branch: 'main',
                    credentialsId: "${env.GITOPS_REPO_CREDENTIALS}",
                    url: "${env.GITOPS_REPO}"
            }
        }

        stage('Update GitOps Deployment') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: "${env.GITOPS_REPO_CREDENTIALS}", 
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
            echo "✅ Docker image built from app repo, pushed, and GitOps repo updated!"
        }
        failure {
            echo "❌ Pipeline failed. Check log"
        }
    }
}

