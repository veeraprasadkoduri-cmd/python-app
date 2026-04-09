pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/veeraprasadkoduri-cmd/python-app.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    echo "=== Workspace structure ==="
                    find . -not -path "*/venv/*" -type f | sort

                    echo "=== Setting up virtualenv ==="
                    cd backend
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip list
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    cd backend
                    . venv/bin/activate
                    python3 -c "import flask, bcrypt, jwt, mysql.connector; print('All imports OK')"
                '''
            }
        }

        stage('Build Artifact') {
            steps {
                sh '''
                    tar --exclude="./backend/venv" \
                        --exclude="./backend/__pycache__" \
                        --exclude="./backend/routes/__pycache__" \
                        --exclude="./backend/.env" \
                        -czf job-app-artifact.tar.gz ./backend
                    echo "=== Artifact ==="
                    ls -lh job-app-artifact.tar.gz
                '''
            }
        }

        stage('Archive Artifact') {
            steps {
                archiveArtifacts artifacts: 'job-app-artifact.tar.gz',
                                 fingerprint: true,
                                 allowEmptyArchive: false
            }
        }
    }

    post {
        success {
            echo "SUCCESS: Pipeline completed."
        }
        failure {
            echo "FAILED: Check logs above."
        }
        always {
            cleanWs()
        }
    }
}
