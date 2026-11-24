// Prueba de integración continua
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
