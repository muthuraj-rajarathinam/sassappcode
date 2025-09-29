pipeline {
    agent any

    environment {
        GIT_CREDENTIALS = 'argocd-id'
        TARGET_REPO = 'https://github.com/muthuraj-rajarathinam/Argocd-connector-saas.git'
        FILE_NAME = "newfile.txt"
    }

    stages {
        stage('Checkout Target Repo') {
            steps {
                git branch: 'main',
                    credentialsId: "${env.GIT_CREDENTIALS}",
                    url: "${env.TARGET_REPO}"
            }
        }

        stage('Create File') {
            steps {
                script {
                    // Use ${} to access Groovy variable
                    sh """
                        echo "This is a new file created by Jenkins on \$(date)" > ${env.FILE_NAME}
                    """
                }
            }
        }

        stage('Commit & Push') {
    steps {
        withCredentials([usernamePassword(
            credentialsId: "${env.GIT_CREDENTIALS}", 
            usernameVariable: 'GITHUB_USERNAME', 
            passwordVariable: 'GITHUB_TOKEN')]) {
                
            sh """
                git config user.email "jenkins@example.com"
                git config user.name "Jenkins CI"
                git add ${env.FILE_NAME}
                git commit -m "Jenkins created ${env.FILE_NAME}"
                git push https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@github.com/muthuraj-rajarathinam/Argocd-connector-saas.git main
            """
        }
    }
}

    }
}
