from dataclasses import asdict
from math import floor, ceil
import math
from typing import List, Optional, Tuple, Dict
from src.domain.value_objects.calculatorresults import CalculatedIndices, Interpretation
from ..value_objects.specification import Specification


class CapabilityCalculator:
    """
    Calcula índices de capacidad basados en especificaciones y estadísticas.
    """
    DPMO_TO_SIGMA_TABLE: Dict[float, float] = {
        3.4: 6.0, 5: 5.92, 8: 5.81, 10: 5.76, 20: 5.61, 30: 5.51, 40: 5.44, 70: 5.31,
        100: 5.22, 150: 5.12, 230: 5.0, 330: 4.91, 480: 4.8, 680: 4.7, 960: 4.6, 
        1350: 4.5, 1860: 4.4, 2550: 4.3, 3460: 4.2, 4660: 4.1, 6210: 4.0, 8190: 3.9,
        10700: 3.8, 13900: 3.7, 17800: 3.6, 22700: 3.5, 28700: 3.4, 35900: 3.3, 
        44600: 3.2, 54800: 3.1, 66800: 3.0, 80800: 2.9, 96800: 2.8, 115000: 2.7,
        135000: 2.6, 158000: 2.5, 184000: 2.4, 212000: 2.3, 242000: 2.2, 274000: 2.1,
        308000: 2.0, 344000: 1.9, 382000: 1.8, 420000: 1.7, 460000: 1.6, 500000: 1.5,
        540000: 1.4, 570000: 1.32, 610000: 1.22, 650000: 1.11, 690000: 1.0, 720000: 0.92,
        750000: 0.83, 780000: 0.73, 810000: 0.62, 840000: 0.51, 860000: 0.42, 
        880000: 0.33, 900000: 0.22, 920000: 0.09
    }
    @staticmethod
    def calculate_indices(
        spec: Specification,
        mean: float,
        std_dev: float,
        raw_measurements: List[float] 
    ) -> CalculatedIndices:

        errors = []
        cp, cr, cpi, cps, cpk, k, tau, cpm = (None,) * 8
        dpmo, yield_value, sigma_level = (None,) * 3
        interp = Interpretation()

        # Validaciones básicas
        if std_dev <= 0:
            errors.append("La desviación estándar debe ser mayor que cero.")
            return CalculatedIndices(errors=errors)
        if spec.tolerance <= 0:
             errors.append("La tolerancia (USL - LSL) debe ser positiva.")
             # Esto ya está validado en Specification, pero doble check no hace daño
             return CalculatedIndices(errors=errors)

        # --- Cálculos ---
        try:
            # Cp & Cr
            cp = spec.tolerance / (6 * std_dev)
            cr = 1 / cp if cp != 0 else float('inf') # Evitar división por cero

            # Cpi & Cps
            cpi = (mean - spec.lsl) / (3 * std_dev)
            cps = (spec.usl - mean) / (3 * std_dev)

            # Cpk
            cpk = min(cpi, cps)

            # K, Tau, Cpm (si N existe)
            if spec.nominal is not None:
                half_tolerance = spec.tolerance / 2
                if half_tolerance > 0:
                   k = ((mean - spec.nominal) / half_tolerance) * 100
                else:
                   k = float('inf') if mean != spec.nominal else 0 # Caso LSL=USL

                variance = std_dev ** 2
                centering_diff_sq = (mean - spec.nominal) ** 2
                tau_squared = variance + centering_diff_sq
                tau = math.sqrt(tau_squared) if tau_squared >= 0 else 0

                if tau > 0:
                    cpm = spec.tolerance / (6 * tau)
                else:
                    # Caso raro: std_dev=0 y mean=nominal
                    cpm = float('inf') if spec.tolerance > 0 else 0 # Infinito si hay tolerancia, 0 si no
            else:
                 k, tau, cpm = None, None, None

            dpmo = CapabilityCalculator.calculate_dpmo(raw_measurements, spec)
            if dpmo is not None:
                # Convertir DPMO a DPO (Defectos Por Oportunidad)
                dpo = dpmo / 1000000
                # Calcular Yield (Rendimiento)
                yield_value = CapabilityCalculator.calculate_yield(dpo)
                # Calcular Nivel Sigma usando la tabla de conversión
                sigma_level = CapabilityCalculator.calculate_sigma_level(dpmo)

        except Exception as e:
            errors.append(f"Error inesperado durante el cálculo: {e}")
            # Podríamos retornar aquí o continuar con la interpretación si hay valores parciales
        try:
            # Determinar el rango de los datos
            min_value = floor(min(raw_measurements))
            max_value = ceil(max(raw_measurements))

            # Definir los intervalos (bins)
            bin_size = 1  # Tamaño de cada intervalo
            bins = list(range(min_value, max_value + bin_size, bin_size))

            # Contar las frecuencias
            counts = [0] * (len(bins) - 1)
            for value in raw_measurements:
                for i in range(len(bins) - 1):
                    if bins[i] <= value < bins[i + 1]:
                        counts[i] += 1
                        break

            # Agregar el último valor al último bin
            if raw_measurements and raw_measurements[-1] == bins[-1]:
                counts[-1] += 1

        except Exception as e:
            errors.append(f"Error al calcular el histograma: {e}")
            bins, counts = [], []
        # --- Interpretación ---
        if cp is not None:
            if cp >= 2.0: interp.cp = "Clase Mundial (>= 2.0)"
            elif cp >= 1.33: interp.cp = "Adecuado (1.33 - 1.99)"
            elif cp >= 1.0: interp.cp = "Parcialmente Adecuado (1.0 - 1.32)"
            elif cp >= 0.67: interp.cp = "No Adecuado (0.67 - 0.99)"
            else: interp.cp = "Requiere Modificaciones Serias (< 0.67)"

        if cpk is not None:
            # Usar 1.33 como umbral común, podría ser configurable
            if cpk >= 1.33: interp.cpk = "Capaz (>= 1.33)"
            elif cpk >= 1.0: interp.cpk = "Parcialmente Capaz (1.0 - 1.32)"
            else: interp.cpk = "No Capaz (< 1.0)"

        if k is not None:
             k_abs = abs(k)
             sign = "derecha" if k > 0 else "izquierda" if k < 0 else "centrado"
             if k_abs <= 20:
                 interp.k = f"Centrado Aceptable (|K| <= 20%, Desv={k:.1f}% {sign})"
             else:
                 interp.k = f"Centrado Inadecuado (|K| > 20%, Desv={k:.1f}% {sign})"

        if cpm is not None and spec.nominal is not None:
            if cpm < 1.0: interp.cpm = "No cumple especificaciones o centrado (< 1.0)"
            elif cpm <= 1.33: interp.cpm = "Cumple especificaciones (1.0 - 1.33), media en tercio central"
            else: interp.cpm = "Cumple especificaciones (> 1.33), media en quinto central"
        elif spec.nominal is None:
             interp.cpm = "N/A (Valor Nominal no proporcionado)"
        if sigma_level is not None:
            if sigma_level >= 6:
                interp.sigma = f"Nivel Six Sigma (σ = {sigma_level:.2f}): Clase mundial"
            elif sigma_level >= 5:
                interp.sigma = f"Nivel Five Sigma (σ = {sigma_level:.2f}): Excelente"
            elif sigma_level >= 4:
                interp.sigma = f"Nivel Four Sigma (σ = {sigma_level:.2f}): Bueno"
            elif sigma_level >= 3:
                interp.sigma = f"Nivel Three Sigma (σ = {sigma_level:.2f}): Aceptable"
            else:
                interp.sigma = f"Nivel Sigma bajo (σ = {sigma_level:.2f}): Requiere mejoras"
                
        if dpmo is not None:
            if dpmo < 10:
                interp.dpmo = f"DPMO muy bajo ({dpmo:.1f}): Excelente"
            elif dpmo < 100:
                interp.dpmo = f"DPMO bajo ({dpmo:.1f}): Muy bueno"
            elif dpmo < 1000:
                interp.dpmo = f"DPMO medio ({dpmo:.1f}): Bueno"
            elif dpmo < 10000:
                interp.dpmo = f"DPMO alto ({dpmo:.1f}): Necesita mejoras"
            else:
                interp.dpmo = f"DPMO muy alto ({dpmo:.1f}): Requiere intervención inmediata"
                
        if yield_value is not None:
            if yield_value > 99.9999:
                interp.yield_value = f"Rendimiento excelente ({yield_value:.4f}%)"
            elif yield_value > 99.99:
                interp.yield_value = f"Rendimiento muy alto ({yield_value:.4f}%)"
            elif yield_value > 99.9:
                interp.yield_value = f"Rendimiento alto ({yield_value:.4f}%)"
            elif yield_value > 99:
                interp.yield_value = f"Rendimiento bueno ({yield_value:.4f}%)"
            elif yield_value > 95:
                interp.yield_value = f"Rendimiento aceptable ({yield_value:.4f}%)"
            else:
                interp.yield_value = f"Rendimiento bajo ({yield_value:.4f}%): Requiere mejoras"

        Interpretation_dict = asdict(interp)
        return CalculatedIndices(
            cp=cp, cr=cr, cpi=cpi, cps=cps, cpk=cpk,
            k=k, tau=tau, cpm=cpm,
             dpmo=dpmo,
            yield_value=yield_value,
            sigma_level=sigma_level,
            interpretation=Interpretation_dict,
            histogram={"bins": bins, "counts": counts}, 
            errors=errors
        )
    
    @staticmethod
    def calculate_dpmo(raw_measurements: List[float], spec: Specification, opportunities_per_unit: int = 1) -> Optional[float]:
        """
        Calcula DPMO (Defectos Por Millón de Oportunidades)
        
        DPMO = (1,000,000 × D) / (U × O)
        
        Donde:
        D = Número de defectos observados
        U = Número de unidades (tamaño de la muestra)
        O = Oportunidades de defecto por unidad
        """
        total_units = len(raw_measurements)
        if total_units == 0:
            return None
        
        # Contar defectos (mediciones fuera de especificación)
        defects = sum(1 for m in raw_measurements 
                     if m < spec.lsl or m > spec.usl)
        
        # Calcular DPMO
        dpmo = (1000000 * defects) / (total_units * opportunities_per_unit)
        return round(dpmo, 2)
    
    @staticmethod
    def calculate_yield(dpo: float) -> Optional[float]:
        """
        Calcula el rendimiento (Yield) del proceso
        
        Yield = (1 - DPO) × 100
        """
        if dpo is None:
            return None
        
        yield_value = (1 - dpo) * 100
        return round(yield_value, 4)
    
    @staticmethod
    def calculate_sigma_level(dpmo: float) -> Optional[float]:
        """
        Calcula el nivel sigma basado en DPMO usando la tabla de conversión
        """
        if dpmo is None:
            return None
            
        # Si DPMO es 0, el nivel sigma es teóricamente 6 o superior
        if dpmo == 0:
            return 6.0
            
        # Encontrar el valor más cercano en la tabla
        closest_dpmo = min(CapabilityCalculator.DPMO_TO_SIGMA_TABLE.keys(), 
                           key=lambda x: abs(x - dpmo))
        
        # Para DPMO mayores que el máximo en la tabla
        if dpmo > 920000:
            return 0.0
            
        return CapabilityCalculator.DPMO_TO_SIGMA_TABLE[closest_dpmo]