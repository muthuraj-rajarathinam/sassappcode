pipeline {
    agent any

    environment {
        GIT_CREDENTIALS = 'e5cc005d-cd56-445b-8396-0cc74487f2d8'  // ID of credentials stored in Jenkins
        TARGET_REPO = 'git@github.com:muthuraj-rajarathinam/Argocd-connector-saas/' 
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
                    sh """
                        echo "This is a new file created by Jenkins on $(date)" > ${FILE_NAME}
                    """
                }
            }
        }

        stage('Commit & Push') {
            steps {
                script {
                    sh """
                        git config user.email "jenkins@example.com"
                        git config user.name "Jenkins CI"
                        git add ${FILE_NAME}
                        git commit -m "Jenkins created ${FILE_NAME}"
                        git push origin main
                    """
                }
            }
        }
    }
}

