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

        stage('Probar arranque del contenedor') {
            steps {
                sh '''
                    docker run -d --name ${IMAGE_NAME}-test \
                        -e FLASK_SECRET_KEY=ci-test-secret \
                        ${IMAGE_NAME}:${BUILD_NUMBER}
                    sleep 5
                    docker exec ${IMAGE_NAME}-test python -c "from urllib.request import urlopen; r=urlopen('http://127.0.0.1:5000/'); print('HTTP:', r.status); assert r.status == 200"
                '''
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
            sh 'docker rm -f ${IMAGE_NAME}-test || true'
            sh 'docker image rm ${IMAGE_NAME}:${BUILD_NUMBER} || true'
        }
    }
}
