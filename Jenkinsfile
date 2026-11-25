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

        stage('Probar aplicacion y base de datos') {
            steps {
                sh '''
                    set -eu

                    NETWORK=ci-network-${BUILD_NUMBER}
                    DB=ci-db-${BUILD_NUMBER}
                    WEB=ci-web-${BUILD_NUMBER}

                    docker network create "$NETWORK"

                    docker run -d --name "$DB" --network "$NETWORK" \
                        -e POSTGRES_DB=registro_db \
                        -e POSTGRES_USER=registro_user \
                        -e POSTGRES_PASSWORD=ci-password \
                        postgres:16-alpine

                    for i in $(seq 1 30); do
                        if docker exec "$DB" pg_isready -U registro_user -d registro_db; then
                            break
                        fi
                        sleep 2
                    done

                    docker exec "$DB" pg_isready -U registro_user -d registro_db

                    docker exec -i "$DB" psql -v ON_ERROR_STOP=1 \
                        -U registro_user -d registro_db < database/init.sql

                    docker run -d --name "$WEB" --network "$NETWORK" \
                        -e DB_HOST="$DB" \
                        -e DB_NAME=registro_db \
                        -e DB_USER=registro_user \
                        -e DB_PASSWORD=ci-password \
                        -e FLASK_SECRET_KEY=ci-test-secret \
                        ${IMAGE_NAME}:${BUILD_NUMBER}

                    sleep 5

                    docker exec "$WEB" python -c "from urllib.request import urlopen; r=urlopen('http://127.0.0.1:5000/'); print('Frontend HTTP:',r.status); assert r.status==200"

                    docker exec "$WEB" python -c "from urllib.request import urlopen; r=urlopen('http://127.0.0.1:5000/api/noticias'); print('API noticias HTTP:',r.status); assert r.status==200"

                    docker exec "$WEB" python -c "from urllib.request import urlopen; r=urlopen('http://127.0.0.1:5000/api/usuarios'); print('API usuarios HTTP:',r.status); assert r.status==200"

                    docker exec "$WEB" python -c "import json; from urllib.request import Request,urlopen; data=json.dumps({'nombre_completo':'Prueba CI','nombre_usuario':'ci${BUILD_NUMBER}'}).encode(); req=Request('http://127.0.0.1:5000/api/usuarios',data=data,headers={'Content-Type':'application/json'},method='POST'); r=urlopen(req); print('Crear usuario HTTP:',r.status); assert r.status==201"
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
            sh '''
                docker rm -f ci-web-${BUILD_NUMBER} ci-db-${BUILD_NUMBER} || true
                docker network rm ci-network-${BUILD_NUMBER} || true
                docker image rm ${IMAGE_NAME}:${BUILD_NUMBER} || true
            '''
        }
    }
}
