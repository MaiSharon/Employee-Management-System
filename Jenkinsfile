pipeline {
    agent any
    environment {
        GIT_CREDENTIALS = '37ae2a82-cefd-4044-8f31-5d40bc2906be'
        GIT_URL = 'git@github.com:MaiSharon/Employee-Management-System.git'
        BRANCH_NAME = 'main'
    }
    stages {
        stage('Checkout') {
            steps {
                script {
                    checkout([
                        $class: 'GitSCM',
                        branches: [[name: "*/${BRANCH_NAME}"]],
                        doGenerateSubmoduleConfigurations: false,
                        extensions: [],
                        submoduleCfg: [],
                        userRemoteConfigs: [[url: GIT_URL, credentialsId: GIT_CREDENTIALS]]
                    ])
                }
            }
        }
        // Other stages here...
    }
}
