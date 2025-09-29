pipeline {
    agent any

    environment {
        APP_REPO = 'https://github.com/muthuraj-rajarathinam/sassappcode.git'
        GITOPS_REPO = 'https://github.com/muthuraj-rajarathinam/Argocd-connector-saas.git'
        GIT_CREDENTIALS = 'argocd-id'                        
        IMAGE_NAME = "muthuraj07/gitapp"        
        DOCKER_CREDENTIALS = 'dockerhub-creds'
        IMAGE_TAG = "${env.BUILD_NUMBER}"
        DEPLOYMENT_FILE = "dev/app-deployment.yaml"
    }

    stages {
        stage('Checkout App Repo') {
            steps {
                git branch: 'main',
                    credentialsId: "sass-code",
                    url: "${APP_REPO}"
            }
        }

        stage('Build & Push Docker Image') {
            steps {
                sh 'ls -l'
                withDockerRegistry([credentialsId: "${DOCKER_CREDENTIALS}", url: '']) {
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
                    credentialsId: "${GIT_CREDENTIALS}",
                    url: "${GITOPS_REPO}"
            }
        }

        stage('Update GitOps Deployment') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: "${GIT_CREDENTIALS}", 
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
            echo "✅ Build, Push & GitOps update completed. ArgoCD will deploy automatically!"
        }
        failure {
            echo "❌ Pipeline failed. Check log"
        }
    }
}

