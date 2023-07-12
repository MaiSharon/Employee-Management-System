pipeline {
    agent any
    environment {
        GIT_CREDENTIALS = "37ae2a82-cefd-4044-8f31-5d40bc2906be"
        GIT_URL = "git@github.com:MaiSharon/Employee-Management-System.git"
        BRANCH_NAME = "main"
        IMAGE_NAME = "ECM-test"
        IMAGE_TAG = "1.0.0"
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
        stage('Build Docker image') {
            steps {
                script {
                    withCredentials([
                        usernamePassword(
                            credentialsId: 'DOCKER_HUB_CREDENTIALS',
                            usernameVariable: 'DOCKER_USERNAME',
                            passwordVariable: 'DOCKER_PASSWORD'
                        )
                    ]) {
                        // 登錄到 Docker Hub
                        sh ('docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD')
                        // 使用 docker 命令根據 Dockerfile 構建 Docker 鏡像
                        def app = docker.build("${IMAGE_NAME}:${IMAGE_TAG}")
                    }
                }
            }
        }
        stage('Test Django Application') {
            steps {
                script {
                    // 啟動 Docker 容器並運行 Django 單元測試
                    docker.image("${IMAGE_NAME}:${IMAGE_TAG}").withRun {c ->
                        sh 'python manage.py test  --settings=settings.local'
                    }
                }
            }
        }
        stage('Start Docker Container') {
            steps {
                script {
                    // 啟動 Docker 容器
                    docker.image("${IMAGE_NAME}:${IMAGE_TAG}").run()
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
