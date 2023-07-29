pipeline {
    agent any
    environment {
        GIT_CREDENTIALS = '37ae2a82-cefd-4044-8f31-5d40bc2906be'
        GIT_URL = 'git@github.com:MaiSharon/Employee-Management-System.git'
        BRANCH_NAME = 'main'
        IMAGE_NAME = 'ECM-test'
        IMAGE_TAG = '1.0.0'
        DOCKER_HUB_CREDENTIALS = 'docker-hub-credentials' // replace with your Docker Hub credentials ID
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
        stage('Build and Push Images') {
            steps {
                script {
                    // Read the docker-compose.yml file
                    def composeFile = readYaml file: 'docker-compose-test.yml'

                    // Loop over services and build and push each one
                    for (service in composeFile.services.keySet()) {
                        echo "Building and pushing $service..."
                        withCredentials([usernamePassword(credentialsId: DOCKER_HUB_CREDENTIALS, passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME')]) {
                            sh "docker build -t ppp300a/$service:${IMAGE_TAG} ."
                            sh "echo ${DOCKER_PASSWORD} | sudo docker login -u ${DOCKER_USERNAME} --password-stdin"
                            sh "sudo docker push ppp300a/$service:${IMAGE_TAG}"
                        }
                    }
                }
            }
        }
    }
}
