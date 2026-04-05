from db import get_connection

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(150) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            skills TEXT,
            location VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(150) NOT NULL,
            company VARCHAR(150) NOT NULL,
            location VARCHAR(100),
            description TEXT,
            skills_required TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            job_id INT NOT NULL,
            status VARCHAR(50) DEFAULT 'sent',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("[DB] Tables initialized successfully.")
