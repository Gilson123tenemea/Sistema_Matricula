# -*- coding: utf-8 -*-
import re


def validar_email(email: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))


def validar_cedula(cedula: str) -> bool:
    """Cedula ecuatoriana: exactamente 10 digitos numericos."""
    return cedula.isdigit() and len(cedula) == 10


def validar_nota(valor: str) -> tuple:
    try:
        n = float(valor.replace(",", "."))
        if 0 <= n <= 10:
            return True, n
        return False, 0.0
    except (ValueError, TypeError):
        return False, 0.0


def validar_creditos(valor: str) -> tuple:
    try:
        c = int(valor)
        if 1 <= c <= 10:
            return True, c
        return False, 0
    except (ValueError, TypeError):
        return False, 0


def validar_telefono(tel: str) -> bool:
    """Valida que el teléfono tenga entre 7 y 15 dígitos (puede tener + al inicio)."""
    t = tel.strip().replace(" ", "").replace("-", "")
    if t.startswith("+"):
        t = t[1:]
    return t.isdigit() and 7 <= len(t) <= 15


def validar_nombre(nombre: str) -> bool:
    """Valida que el nombre tenga al menos 3 chars y solo letras/espacios."""
    return len(nombre.strip()) >= 3 and bool(re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\.\-]+$",
                                                        nombre.strip()))


def validar_codigo(codigo: str) -> bool:
    """Valida que el código tenga entre 3 y 20 chars alfanuméricos."""
    return bool(re.match(r"^[A-Za-z0-9\-_]{3,20}$", codigo.strip()))


def sanitizar_texto(texto: str) -> str:
    """Elimina caracteres potencialmente problemáticos."""
    return texto.strip()
