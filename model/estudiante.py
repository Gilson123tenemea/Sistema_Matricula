# -*- coding: utf-8 -*-


class Estudiante:
    """Modelo de estudiante universitario."""

    def __init__(self, cedula: str, nombre: str, edad: int,
                 carrera: str, email: str, semestre: int = 1):
        self.cedula   = cedula
        self.nombre   = nombre
        self.edad     = edad
        self.carrera  = carrera
        self.email    = email
        self.semestre = semestre

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(d):
        return Estudiante(**d)

    def __repr__(self):
        return f"Estudiante({self.cedula}, {self.nombre})"
