# -*- coding: utf-8 -*-
"""
model/horario.py
Un Horario es un GRUPO de bloques semanales para una asignatura.
Ej: "Lunes 07:00-09:00 + Miércoles 07:00-09:00" = 4h semanales para 4 créditos.
"""

DIAS_VALIDOS = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado"]
HORAS_VALIDAS = [f"{h:02d}:00" for h in range(7, 22)]


class BloqueHorario:
    """Un bloque = un día + hora inicio + hora fin."""
    def __init__(self, dia: str, hora_inicio: str, hora_fin: str):
        self.dia         = dia
        self.hora_inicio = hora_inicio  # "HH:MM"
        self.hora_fin    = hora_fin     # "HH:MM"

    def horas(self) -> float:
        """Duración en horas del bloque."""
        hi = int(self.hora_inicio.split(":")[0])
        hf = int(self.hora_fin.split(":")[0])
        return hf - hi

    def solapado(self, otro: "BloqueHorario") -> bool:
        """True si este bloque se solapa con otro en el mismo día."""
        if self.dia != otro.dia:
            return False
        hi1 = int(self.hora_inicio.split(":")[0])
        hf1 = int(self.hora_fin.split(":")[0])
        hi2 = int(otro.hora_inicio.split(":")[0])
        hf2 = int(otro.hora_fin.split(":")[0])
        return hi1 < hf2 and hi2 < hf1

    def __str__(self):
        return f"{self.dia} {self.hora_inicio}–{self.hora_fin}"

    def to_dict(self):
        return {"dia": self.dia, "hi": self.hora_inicio, "hf": self.hora_fin}

    @staticmethod
    def from_dict(d):
        return BloqueHorario(d["dia"], d["hi"], d["hf"])


class Horario:
    """
    Grupo de bloques semanales asociado a una asignatura.
    Ejemplo: id=1, aula="Aula 101", bloques=[Lunes 7-9, Viernes 7-9]
    """
    def __init__(self, id: int, bloques: list = None, aula: str = "Por asignar"):
        self.id     = id
        self.bloques: list[BloqueHorario] = bloques or []
        self.aula   = aula

    def horas_semanales(self) -> float:
        return sum(b.horas() for b in self.bloques)

    def resumen(self) -> str:
        if not self.bloques:
            return "(sin bloques)"
        return " + ".join(str(b) for b in self.bloques)

    def label(self) -> str:
        return f"[{self.id}] {self.resumen()} | {self.aula}"

    def tiene_conflicto_con(self, otro: "Horario") -> bool:
        """True si algún bloque de este horario choca con alguno del otro."""
        for b1 in self.bloques:
            for b2 in otro.bloques:
                if b1.solapado(b2):
                    return True
        return False

    def bloques_str(self) -> str:
        """Serializa bloques a string para la DB: 'Lunes|07:00|09:00;Viernes|07:00|09:00'"""
        return ";".join(f"{b.dia}|{b.hora_inicio}|{b.hora_fin}"
                        for b in self.bloques)

    @staticmethod
    def bloques_from_str(s: str) -> list:
        """Deserializa bloques desde string de la DB."""
        if not s:
            return []
        result = []
        for part in s.split(";"):
            parts = part.strip().split("|")
            if len(parts) == 3:
                result.append(BloqueHorario(parts[0], parts[1], parts[2]))
        return result

    def __str__(self):
        return self.resumen()
