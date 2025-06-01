from typing import Optional, List
from mysql.connector import Error as MySQLError
from src.domain.entities.process import Process
from src.domain.repositories.process_repository import IProcessRepository
from ..database.mysql import get_db_connection

class MySQLProcessRepository(IProcessRepository):
    """
    Implementación de IProcessRepository utilizando MySQL
    """
    
    def save(self, process: Process) -> None:
        """Guarda un nuevo proceso o actualiza uno existente"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Verificar si ya existe (actualización)
            cursor.execute("SELECT id FROM processes WHERE id = %s", (process.id,))
            exists = cursor.fetchone() is not None
            
            if exists:
                # Actualizar proceso existente
                cursor.execute(
                    "UPDATE processes SET name = %s, description = %s WHERE id = %s",
                    (process.name, process.description, process.id)
                )
            else:
                # Insertar nuevo proceso
                cursor.execute(
                    "INSERT INTO processes (id, name, description) VALUES (%s, %s, %s)",
                    (process.id, process.name, process.description)
                )
                
            conn.commit()
            
        except MySQLError as err:
            conn.rollback()
            print(f"MySQL error: {err}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def find_by_id(self, process_id: str) -> Optional[Process]:
        """Busca un proceso por su ID"""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("SELECT * FROM processes WHERE id = %s", (process_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
                
            # Crear y retornar el proceso
            return Process(
                name=row["name"],
                description=row["description"],
                id=row["id"]
            )
            
        except MySQLError as err:
            print(f"MySQL error: {err}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def find_all(self) -> List[Process]:
        """Devuelve todos los procesos"""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("SELECT * FROM processes")
            processes = []
            
            for row in cursor.fetchall():
                process = Process(
                    name=row["name"],
                    description=row["description"],
                    id=row["id"]
                )
                processes.append(process)
                
            return processes
            
        except MySQLError as err:
            print(f"MySQL error: {err}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def delete(self, process_id: str) -> bool:
        """Elimina un proceso por su ID"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM processes WHERE id = %s", (process_id,))
            deleted = cursor.rowcount > 0
            conn.commit()
            return deleted
            
        except MySQLError as err:
            conn.rollback()
            print(f"MySQL error: {err}")
            raise
        finally:
            cursor.close()
            conn.close()