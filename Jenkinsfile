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
        stage('Check Docker CLI') {
            steps {
                script {
                    // 檢查 Docker CLI 版本
                    sh 'docker --version'
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
                        // 使用yml文件製作image
                        sh 'docker-compose -f docker-compose-build.yml build'
                    }
                }
            }
        }
        stage('Test Django Application') {
            steps {
                script {
                    // 啟動 Docker 容器並運行 Django 單元測試
                    sh 'docker-compose -f docker-compose-build.yml run --rm web python manage.py test  --settings=settings.local'
                    }
                }
            }
        }
        stage('Start Docker Container') {
            steps {
                script {
                    // 啟動 Docker 容器
                    sh 'docker-compose -f docker-compose-build.yml up -d'
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
