# -*- coding: utf-8 -*-


class Docente:
    """Modelo de docente universitario."""

    def __init__(self, cedula: str, nombres: str, titulo: str,
                 email: str, especialidad: str, telefono: str):
        self.cedula       = cedula
        self.nombres      = nombres
        self.titulo       = titulo
        self.email        = email
        self.especialidad = especialidad
        self.telefono     = telefono

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(d):
        return Docente(**d)

    def __repr__(self):
        return f"Docente({self.cedula}, {self.nombres})"
