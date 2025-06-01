from typing import Optional, List , Dict
from datetime import datetime
from mysql.connector import Error as MySQLError
from src.domain.entities.capacity_study import CapacityStudy, InputDataSummary
from src.domain.value_objects.calculatorresults import CalculatedIndices
from src.domain.repositories.capacity_study_repository import ICapacityStudyRepository
from src.infraestructure.persistence.database.mysql import get_db_connection
import json
class MySQLCapacityStudyRepository(ICapacityStudyRepository):
    """
    Implementación de ICapacityStudyRepository utilizando MySQL
    """
    
    def save(self, study: CapacityStudy) -> CapacityStudy:
        """Guarda un estudio de capacidad en la base de datos"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Convertir las estructuras complejas a JSON para almacenamiento
            interpretation_json = json.dumps(study.interpretation) if study.interpretation else None
            histogram_json = json.dumps(study.histogram) if study.histogram else None
            
            # Verificar si ya existe
            cursor.execute("SELECT id FROM capacity_studies WHERE id = %s", (study.id,))
            exists = cursor.fetchone() is not None
            
            if exists:
                # Actualizar
                cursor.execute("""
                    UPDATE capacity_studies 
                    SET ctq_id = %s, study_date = %s, 
                        mean = %s, std_dev = %s, sample_size = %s,
                        cp = %s, cr = %s, cpi = %s, cps = %s, cpk = %s, k = %s, cpm = %s,
                        dpmo = %s, yield_value = %s, sigma_level = %s,
                        interpretation = %s, histogram = %s
                    WHERE id = %s
                """, (
                    study.ctq_id, study.study_date, 
                    study.mean, study.std_dev, study.sample_size,
                    study.cp, study.cr, study.cpi, study.cps, study.cpk, study.k, study.cpm,
                    study.dpmo, study.yield_value, study.sigma_level,
                    interpretation_json, histogram_json,
                    study.id
                ))
            else:
                # Insertar nuevo
                cursor.execute("""
                    INSERT INTO capacity_studies (
                        id, ctq_id, study_date, 
                        mean, std_dev, sample_size,
                        cp, cr, cpi, cps, cpk, k, cpm,
                        dpmo, yield_value, sigma_level,
                        interpretation, histogram
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    study.id, study.ctq_id, study.study_date, 
                    study.mean, study.std_dev, study.sample_size,
                    study.cp, study.cr, study.cpi, study.cps, study.cpk, study.k, study.cpm,
                    study.dpmo, study.yield_value, study.sigma_level,
                    interpretation_json, histogram_json
                ))
                
            conn.commit()
            return study
            
        except MySQLError as e:
            conn.rollback()
            print(f"Error MySQL: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def _dict_to_entity(self, data: Dict) -> CapacityStudy:
        """Convierte un diccionario de la base de datos a una entidad CapacityStudy"""
        # Parsear los campos JSON
        interpretation = json.loads(data.get('interpretation')) if data.get('interpretation') else {}
        histogram = json.loads(data.get('histogram')) if data.get('histogram') else {"bins": [], "counts": []}
        
        study = CapacityStudy(
            id=data.get('id'),
            ctq_id=data.get('ctq_id'),
            study_date=data.get('study_date')
        )
        
        # Asignar estadísticas
        study.mean = data.get('mean')
        study.std_dev = data.get('std_dev')
        study.sample_size = data.get('sample_size')
        
        # Asignar índices tradicionales
        study.cp = data.get('cp')
        study.cr = data.get('cr')
        study.cpi = data.get('cpi')
        study.cps = data.get('cps')
        study.cpk = data.get('cpk')
        study.k = data.get('k')
        study.cpm = data.get('cpm')
        
        # Asignar nuevos índices Six Sigma
        study.dpmo = data.get('dpmo')
        study.yield_value = data.get('yield_value')
        study.sigma_level = data.get('sigma_level')
        
        # Asignar metadatos
        study.interpretation = interpretation
        study.histogram = histogram
        
        return study
    
    def find_by_id(self, study_id: str) -> Optional[CapacityStudy]:
        """Busca un estudio de capacidad por su ID"""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("SELECT * FROM capacity_studies WHERE id = %s", (study_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            # Crear InputDataSummary
            input_data = InputDataSummary(
                mean=row["mean"],
                std_dev=row["std_dev"],
                sample_size=row["sample_size"]
            )
            
            # Crear CalculatedIndices
            results = CalculatedIndices(
                cp=row["cp"],
                cr=row["cr"],
                cpi=row["cpi"],
                cps=row["cps"],
                cpk=row["cpk"],
                k=row["k"],
                cpm=row["cpm"]
            )
            
            # Crear y devolver el estudio
            return CapacityStudy(
                ctq_id=row["ctq_id"],
                input_data=input_data,
                id=row["id"],
                study_date=row["study_date"],
                results=results
            )
            
        except MySQLError as err:
            print(f"MySQL error: {err}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def find_by_ctq_id(self, ctq_id: str) -> List[CapacityStudy]:
        """Busca estudios asociados a una CTQ específica"""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("SELECT * FROM capacity_studies WHERE ctq_id = %s ORDER BY study_date DESC", (ctq_id,))
            studies = []
            
            for row in cursor.fetchall():
                input_data = InputDataSummary(
                    mean=row["mean"],
                    std_dev=row["std_dev"],
                    sample_size=row["sample_size"]
                )
                
                results = CalculatedIndices(
                    cp=row["cp"],
                    cr=row["cr"],
                    cpi=row["cpi"],
                    cps=row["cps"],
                    cpk=row["cpk"],
                    k=row["k"],
                    cpm=row["cpm"]
                )
                
                study = CapacityStudy(
                    ctq_id=row["ctq_id"],
                    input_data=input_data,
                    id=row["id"],
                    study_date=row["study_date"],
                    results=results
                )
                studies.append(study)
                
            return studies
            
        except MySQLError as err:
            print(f"MySQL error: {err}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def delete(self, study_id: str) -> bool:
        """Elimina un estudio por su ID"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM capacity_studies WHERE id = %s", (study_id,))
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
            
    def find_all(self) -> List[CapacityStudy]:
        """Devuelve todos los estudios"""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("SELECT * FROM capacity_studies ORDER BY study_date DESC")
            studies = []
            
            for row in cursor.fetchall():
                input_data = InputDataSummary(
                    mean=row["mean"],
                    std_dev=row["std_dev"],
                    sample_size=row["sample_size"]
                )
                
                results = CalculatedIndices(
                    cp=row["cp"],
                    cr=row["cr"],
                    cpi=row["cpi"],
                    cps=row["cps"],
                    cpk=row["cpk"],
                    k=row["k"],
                    cpm=row["cpm"]
                )
                
                study = CapacityStudy(
                    ctq_id=row["ctq_id"],
                    input_data=input_data,
                    id=row["id"],
                    study_date=row["study_date"],
                    results=results
                )
                studies.append(study)
                
            return studies
            
        except MySQLError as err:
            print(f"MySQL error: {err}")
            raise
        finally:
            cursor.close()
            conn.close()