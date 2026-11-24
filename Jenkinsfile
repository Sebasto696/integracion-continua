pipeline {
    agent any

    environment {
        IMAGE_NAME = 'integracion-virtual-web'
    }

    stages {
        stage('Descargar codigo') {
            steps {
                checkout scm
            }
        }

        stage('Compilar frontend Angular') {
            steps {
                dir('frontend') {
                    sh 'npm ci'
                    sh 'npm run build'
                }
            }
        }

        stage('Construir imagen Docker') {
            steps {
                sh 'docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} ./app'
            }
        }

        stage('Validar aplicacion') {
            steps {
                sh 'docker run --rm ${IMAGE_NAME}:${BUILD_NUMBER} python -m compileall -q app.py'
            }
        }
    }

    post {
        always {
            sh 'docker image rm ${IMAGE_NAME}:${BUILD_NUMBER} || true'
        }
    }
}
