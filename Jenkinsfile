pipeline {
    agent any

    environment {
        DOCKERHUB_CREDS = credentials('dockerhub-creds')
        IMAGE_UNSTABLE = "zarman53/sentiment-api:unstable"
        IMAGE_STABLE = "zarman53/sentiment-api:stable"
        NETWORK_NAME = "sentiment-net-${BUILD_NUMBER}"
        APP_CONTAINER = "sentiment-app-${BUILD_NUMBER}"
        CHROME_CONTAINER = "chrome-test-${BUILD_NUMBER}"
    }

    stages {
        stage('Fetch') {
            steps {
                checkout scm
            }
        }

        stage('Build and Run') {
            steps {
                sh '''
                    docker build -t ${IMAGE_UNSTABLE} .
                    docker network create ${NETWORK_NAME} || true
                    docker rm -f ${APP_CONTAINER} || true
                    docker run -d --name ${APP_CONTAINER} --network ${NETWORK_NAME} ${IMAGE_UNSTABLE}
                    sleep 10
                    echo "Container started"
                '''
            }
        }

        stage('Unit Test') {
            steps {
                sh '''
                    docker run --rm \
                        --network ${NETWORK_NAME} \
                        -e BASE_URL=http://${APP_CONTAINER}:5000 \
                        -v ${WORKSPACE}/tests:/tests \
                        python:3.10-slim \
                        sh -c "pip install --quiet requests pytest && python -m pytest /tests/test_api.py -v"
                '''
            }
        }

        stage('UI Test') {
            steps {
                sh '''
                    docker rm -f ${CHROME_CONTAINER} || true
                    docker run -d --name ${CHROME_CONTAINER} --network ${NETWORK_NAME} selenium/standalone-chrome:latest
                    sleep 8

                    docker run --rm \
                        --network ${NETWORK_NAME} \
                        -e BASE_URL=http://${APP_CONTAINER}:5000 \
                        -e SELENIUM_REMOTE_URL=http://${CHROME_CONTAINER}:4444/wd/hub \
                        -v ${WORKSPACE}/tests:/tests \
                        python:3.10-slim \
                        sh -c "pip install --quiet selenium pytest && python -m pytest /tests/test_ui.py -v"
                '''
            }
        }

        stage('Build and Push') {
            steps {
                sh '''
                    rm -rf /tmp/stable-build-${BUILD_NUMBER}
                    git clone -b stable-fallback https://github.com/ZarmanSattar/selfhealing-mlops-FA23-BAI-053.git /tmp/stable-build-${BUILD_NUMBER}
                    docker build -t ${IMAGE_STABLE} /tmp/stable-build-${BUILD_NUMBER}

                    echo "${DOCKERHUB_CREDS_PSW}" | docker login -u "${DOCKERHUB_CREDS_USR}" --password-stdin
                    docker push ${IMAGE_UNSTABLE}
                    docker push ${IMAGE_STABLE}
                '''
            }
        }

        stage('Deploy to Minikube') {
            steps {
                sh '''
                    kubectl apply -f k8s/pvc.yaml
                    kubectl apply -f k8s/blue-deployment.yaml
                    kubectl apply -f k8s/green-deployment.yaml
                    kubectl apply -f k8s/service.yaml
                '''
            }
        }
    }

    post {
        always {
            sh '''
                docker rm -f ${APP_CONTAINER} ${CHROME_CONTAINER} || true
                docker network rm ${NETWORK_NAME} || true
                rm -rf /tmp/stable-build-${BUILD_NUMBER}
            '''
        }
    }
}
