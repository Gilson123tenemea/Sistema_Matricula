# -*- coding: utf-8 -*-


class Asignatura:
    """Modelo de asignatura con cupo, ciclo, prerequisito y horas semanales."""

    def __init__(self, codigo: str, nombre: str, docente: str,
                 creditos: int, cupo_maximo: int = 30,
                 semestre: int = 1, prerequisito: str = None,
                 carrera: str = "", horario_id: int = None,
                 horas_semanales: int = None):
        self.codigo          = codigo
        self.nombre          = nombre
        self.docente         = docente      # cedula del docente asignado
        self.creditos        = creditos
        self.cupo_maximo     = cupo_maximo
        self.semestre        = semestre     # ciclo (1..10)
        self.prerequisito    = prerequisito
        self.carrera         = carrera
        self.horario_id      = horario_id
        # horas_semanales: por defecto = creditos (1 crédito ≈ 1h/semana)
        self.horas_semanales = horas_semanales or creditos

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(d):
        return Asignatura(**d)

    def __repr__(self):
        return f"Asignatura({self.codigo}, {self.nombre})"
