import mysql.connector
import os

def init_database():
    """Inicializa la base de datos creando las tablas necesarias"""
    # Conectar a MySQL sin especificar base de datos
    conn = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        port=int(os.getenv("DB_PORT", "3306")),  # Añadido el puerto
        connection_timeout=30
    )
    
    cursor = conn.cursor()
    db_name = os.getenv("MYSQL_DATABASE", "kpib")
    
    try:
        # Crear la base de datos si no existe
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute(f"USE {db_name}")
        
        # Crear tabla de procesos
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS processes (
            id VARCHAR(50) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Crear tabla de CTQs
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ctqs (
            id VARCHAR(50) PRIMARY KEY,
            process_id VARCHAR(50) NOT NULL,
            name VARCHAR(255) NOT NULL,
            unit VARCHAR(50),
            usl DOUBLE NOT NULL,
            lsl DOUBLE NOT NULL,
            nominal DOUBLE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (process_id) REFERENCES processes(id) ON DELETE CASCADE,
            CONSTRAINT chk_usl_gt_lsl CHECK (usl > lsl)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Crear tabla de estudios de capacidad
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS capacity_studies (
            id VARCHAR(50) PRIMARY KEY,
            ctq_id VARCHAR(50) NOT NULL,
            study_date TIMESTAMP NOT NULL,
            sample_size INT,
            mean DOUBLE,
            std_dev DOUBLE,
            cp DOUBLE,
            cr DOUBLE,
            cpi DOUBLE,
            cps DOUBLE,
            cpk DOUBLE,
            k DOUBLE,
            cpm DOUBLE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ctq_id) REFERENCES ctqs(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Crear índices para mejorar rendimiento
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_capacity_studies_ctq_id ON capacity_studies (ctq_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_capacity_studies_study_date ON capacity_studies (study_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ctqs_process_id ON ctqs (process_id)")
        
        conn.commit()
        print(f"Base de datos {db_name} inicializada correctamente")
        
    except mysql.connector.Error as err:
        print(f"Error al inicializar la base de datos: {err}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    init_database()