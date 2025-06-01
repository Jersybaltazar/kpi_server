from typing import Optional, List
from mysql.connector import Error as MySQLError
from src.domain.entities.ctq import CTQ
from src.domain.value_objects.specification import Specification
from src.domain.repositories.ctq_repository import ICTQRepository
from ..database.mysql import get_db_connection

class MySQLCTQRepository(ICTQRepository):
    """
    Implementación de ICTQRepository utilizando MySQL
    """
    
    def save(self, ctq: CTQ) -> None:
        """Guarda una nueva CTQ o actualiza una existente"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Verificar si ya existe (actualización)
            cursor.execute("SELECT id FROM ctqs WHERE id = %s", (ctq.id,))
            exists = cursor.fetchone() is not None
            
            if exists:
                # Actualizar CTQ existente
                cursor.execute(
                    """UPDATE ctqs 
                       SET process_id = %s, name = %s, unit = %s, 
                           usl = %s, lsl = %s, nominal = %s
                       WHERE id = %s""",
                    (ctq.process_id, ctq.name, ctq.unit, 
                     ctq.specification.usl, ctq.specification.lsl, ctq.specification.nominal,
                     ctq.id)
                )
            else:
                # Insertar nueva CTQ
                cursor.execute(
                    """INSERT INTO ctqs 
                       (id, process_id, name, unit, usl, lsl, nominal) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (ctq.id, ctq.process_id, ctq.name, ctq.unit,
                     ctq.specification.usl, ctq.specification.lsl, ctq.specification.nominal)
                )
                
            conn.commit()
            
        except MySQLError as err:
            conn.rollback()
            print(f"MySQL error: {err}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def find_by_id(self, ctq_id: str) -> Optional[CTQ]:
        """Busca una CTQ por su ID"""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT ctqs.*, processes.name AS process_name
                FROM ctqs
                JOIN processes ON ctqs.process_id = processes.id
                WHERE ctqs.id = %s
            """, (ctq_id,))
            row = cursor.fetchone()
        
            
            if not row:
                return None
                
            # Crear objeto Specification
            spec = Specification(
                usl=row["usl"],
                lsl=row["lsl"],
                nominal=row["nominal"]
            )
            
            # Crear y retornar la CTQ
            return CTQ(
                process_id=row["process_id"],
                name=row["name"],
                unit=row["unit"],
                specification=spec,
                id=row["id"],
                process_name=row["process_name"]  # Asumiendo que quieres el nombre del proceso también
            )
            
        except MySQLError as err:
            print(f"MySQL error: {err}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def find_all(self) -> List[CTQ]:
        """Devuelve todas las CTQs"""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("SELECT * FROM ctqs")
            ctqs = []
            
            for row in cursor.fetchall():
                spec = Specification(
                    usl=row["usl"],
                    lsl=row["lsl"],
                    nominal=row["nominal"]
                )
                
                ctq = CTQ(
                    process_id=row["process_id"],
                    name=row["name"],
                    unit=row["unit"],
                    specification=spec,
                    id=row["id"]
                )
                ctqs.append(ctq)
                
            return ctqs
            
        except MySQLError as err:
            print(f"MySQL error: {err}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def find_by_process_id(self, process_id: str) -> List[CTQ]:
        """Busca CTQs asociadas a un proceso específico"""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("SELECT * FROM ctqs WHERE process_id = %s", (process_id,))
            ctqs = []
            
            for row in cursor.fetchall():
                spec = Specification(
                    usl=row["usl"],
                    lsl=row["lsl"],
                    nominal=row["nominal"]
                )
                
                ctq = CTQ(
                    process_id=row["process_id"],
                    name=row["name"],
                    unit=row["unit"],
                    specification=spec,
                    id=row["id"]
                )
                ctqs.append(ctq)
                
            return ctqs
            
        except MySQLError as err:
            print(f"MySQL error: {err}")
            raise
        finally:
            cursor.close()
            conn.close()