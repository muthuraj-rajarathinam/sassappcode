pipeline {
    agent any

    environment {
        IMAGE = "username/buzzgen:${env.BUILD_NUMBER}"   // unique tag
    }

    stages {
        stage('Build & Push Image') {
            steps {
                sh """
                docker build -t $IMAGE .
                echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin
                docker push $IMAGE
                """
            }
        }

        stage('Update GitOps Repo') {
            steps {
                sh """
                git clone https://github.com/muthuraj-rajarathinam/Argocd-connector-saas.git
                cd my-gitops-repo/dev
                sed -i "s|image: .*|image: $IMAGE|g" app-deployment.yaml
                git config user.name "jenkins"
                git config user.email "jenkins@ci"
                git add app-deployment.yaml
                git commit -m "update image to $IMAGE"
                git push https://$GIT_USERNAME:$GIT_PASSWORD@github.com/muthuraj-rajarathinam/Argocd-connector-saas.git
                """
            }
        }
    }
}
