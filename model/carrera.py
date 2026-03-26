# -*- coding: utf-8 -*-


class Carrera:
    """Modelo de carrera universitaria."""

    def __init__(self, codigo: str, nombre: str, num_ciclos: int = 8,
                 descripcion: str = ""):
        self.codigo      = codigo
        self.nombre      = nombre
        self.num_ciclos  = num_ciclos
        self.descripcion = descripcion

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(d):
        return Carrera(**d)

    def __repr__(self):
        return f"Carrera({self.codigo}, {self.nombre})"
