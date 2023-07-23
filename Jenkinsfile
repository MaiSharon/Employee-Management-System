pipeline {
    agent any
    environment {
        GIT_CREDENTIALS = "37ae2a82-cefd-4044-8f31-5d40bc2906be"
        GIT_URL = "git@github.com:MaiSharon/Employee-Management-System.git"
        BRANCH_NAME = "main"
        IMAGE_NAME = "ECM-test"
        IMAGE_TAG = "1.0.0"
        ENV_JENKINS = "/var/jenkins_home/workspace/pull"
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
                    // 检查 Docker CLI 版本
                    sh '''
                    sudo docker version
                    sudo docker compose version
                    '''
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
                        // 使用 docker-compose 文件构建镜像
                        sh ('sudo docker build -t testtt:$IMAGE_TAG -f test-Dockerfile .')
                    }
                }
            }
        }
        stage('Start Docker Container') {
            steps {
                script {
                    // Start the web Docker container while simultaneously running the 'start.local.sh' script.
                    sh "sudo docker compose -f docker-compose-build.yml run --rm web /bin/sh -c '${ENV_JENKINS}/start.local.sh'"
                }
            }
        }

        stage('Test Django Application') {
            steps {
                script {
                    // Run automated testing
                    sh "sudo docker compose -f docker-compose-build.yml run --rm web /bin/sh -c '${ENV_JENKINS}/start.local.sh && python manage.py test --settings=settings.local'"

                }
            }
        }

        stage('Start Docker Container') {
            steps {
                script {
                    // 启动 Docker 容器
                    sh "sudo docker run -d --name web ppp300a/dept-dev:1.2.0 /bin/sh ${ENV_JENKINS}/start.local.sh"
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
