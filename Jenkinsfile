pipeline {
    agent any
    environment {
        GIT_CREDENTIALS = "37ae2a82-cefd-4044-8f31-5d40bc2906be"
        GIT_URL = "git@github.com:MaiSharon/Employee-Management-System.git"
        BRANCH_NAME = "main"
        IMAGE_NAME = "ECM-test"
        IMAGE_TAG = "1.0.0"
        // 依據Dockerfile的WORKDIR設定一樣
        ENV_JENKINS = "/data/prj_dept"
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
        stage('Check Docker CLI and Docker compose') {
            steps {
                script {
                    // 检查 Docker CLI 版本
                    sh '''
                    sudo docker version
                    sudo docker compose version
                    '''
                }
            }
        }
        stage('Start Docker Container') {
            steps {
                script {
                    // Run automated testing
                    sh "sudo docker compose -f docker-compose-test.yml run --rm web /bin/sh -c 'python manage.py test --settings=settings.local'"

                    // Ensure the containers are running
                    sh "sudo docker compose -f docker-compose-test.yml down"
                }
            }
        }

        stage('Test Django Application') {
            steps {
                script {


                    // Stop all the containers after testing
                    sh "sudo docker compose -f docker-compose-test.yml down"
                }
            }
        }

        stage('Start Web Container') {
            steps {
                script {
                    // 启动 Docker 容器
                    sh "sudo docker compose -f docker-compose-test.yml up -d"
                }
            }
        }
    }
    post {
        always {
            // 总是在 pipeline 结束后执行的步骤
            sh 'echo "Pipeline has finished"'
        }
        success {
            // 只有在 pipeline 成功结束后才执行的步骤
            sh 'echo "Pipeline completed successfully"'
        }
        failure {
            // 只有在 pipeline 失败后才执行的步骤
            sh 'echo "Pipeline failed"'
        }
    }
}
