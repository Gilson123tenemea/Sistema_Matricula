# -*- coding: utf-8 -*-
import hashlib


class Usuario:
    """Modelo de usuario del sistema (Admin, Docente o Estudiante)."""

    ROLES = ("admin", "docente", "estudiante")

    def __init__(self, username: str, password_hash: str,
                 rol: str, cedula_vinculada: str = None,
                 # Alias para compatibilidad
                 cedula_estudiante: str = None):
        self.username         = username
        self.password_hash    = password_hash
        self.rol              = rol  # "admin" | "docente" | "estudiante"
        # cedula_vinculada puede contener cedula de docente o estudiante
        self.cedula_vinculada = cedula_vinculada or cedula_estudiante

    @property
    def cedula_estudiante(self):
        """Alias para compatibilidad con código anterior."""
        return self.cedula_vinculada if self.rol == "estudiante" else None

    @staticmethod
    def hash_password(plain: str) -> str:
        return hashlib.sha256(plain.encode()).hexdigest()

    def verificar_password(self, plain: str) -> bool:
        return self.password_hash == Usuario.hash_password(plain)

    def es_admin(self) -> bool:
        return self.rol == "admin"

    def es_docente(self) -> bool:
        return self.rol == "docente"

    def es_estudiante(self) -> bool:
        return self.rol == "estudiante"
