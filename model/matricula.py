# -*- coding: utf-8 -*-
from utils.constants import NOTA_MINIMA_APROBACION, PERIODO


class Matricula:
    """Relación entre Estudiante y Asignatura con nota y periodo."""

    def __init__(self, estudiante, asignatura, nota: float,
                 periodo: str = None):
        self.estudiante = estudiante
        self.asignatura = asignatura
        self.nota       = nota
        self.periodo    = periodo or f"{PERIODO[0]}-{PERIODO[1]}"

    def estado(self) -> str:
        return "Aprobado" if self.nota >= NOTA_MINIMA_APROBACION else "Reprobado"

    def to_dict(self):
        return {
            "cedula":  self.estudiante.cedula,
            "codigo":  self.asignatura.codigo,
            "nota":    self.nota,
            "periodo": self.periodo,
        }
