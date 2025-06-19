# Esta es la misma función que hice en la tarea APA-T6, la reutilizo.
# Importo esta en normaliza.py, que es el que hace las fuinciones tkinter 

import re

def normalizaHoras(ficText, ficNorm):
    patrones = [
        # HH:MM
        (re.compile(r'\b(\d{1,2}):(\d{2})\b'),
         lambda m: f'{int(m.group(1)):02}:{int(m.group(2)):02}'
         if 0 <= int(m.group(1)) < 24 and 0 <= int(m.group(2)) < 60 else m.group(0)),

        # 8h45m
        (re.compile(r'\b(\d{1,2})h(\d{1,2})m\b'),
         lambda m: f'{int(m.group(1)):02}:{int(m.group(2)):02}'
         if 0 <= int(m.group(1)) < 24 and 0 <= int(m.group(2)) < 60 else m.group(0)),

        # 8h
        (re.compile(r'\b(\d{1,2})h\b'),
         lambda m: f'{int(m.group(1)):02}:00'
         if 0 <= int(m.group(1)) < 24 else m.group(0)),

        # Verbales
        (re.compile(r'\b(\d{1,2}) y media de la tarde\b'),
         lambda m: f'{(int(m.group(1)) + 12) % 24:02}:30'),

        (re.compile(r'\b(\d{1,2}) y cuarto de la tarde\b'),
         lambda m: f'{(int(m.group(1)) + 12) % 24:02}:15'),

        (re.compile(r'\b(\d{1,2}) menos cuarto de la tarde\b'),
         lambda m: f'{(int(m.group(1)) + 11) % 24:02}:45'),

        # 7h de la mañana
        (re.compile(r'\b(\d{1,2})h de la mañana\b'),
         lambda m: f'{int(m.group(1)) % 12:02}:00'),

        # 12 de la noche
        (re.compile(r'\b12 de la noche\b'), lambda m: '00:00'),

        # Extras
        (re.compile(r'\b(\d{1,2}) en punto\b'),
         lambda m: f'{int(m.group(1)) % 12 or 12:02}:00'),

        (re.compile(r'\b(\d{1,2}) y media\b'),
         lambda m: f'{int(m.group(1)) % 12 or 12:02}:30'),

        (re.compile(r'\b(\d{1,2}) y cuarto\b'),
         lambda m: f'{int(m.group(1)) % 12 or 12:02}:15'),

        (re.compile(r'\b(\d{1,2}) menos cuarto\b'),
         lambda m: f'{(int(m.group(1)) - 1) % 12 or 12:02}:45'),
    ]

    with open(ficText, 'r', encoding='utf-8') as entrada, open(ficNorm, 'w', encoding='utf-8') as salida:
        for linea in entrada:
            for patron, reemplazo in patrones:
                linea = patron.sub(reemplazo, linea)
            salida.write(linea)

if __name__ == "__main__":
    normalizaHoras("horas.txt", "horas_normalizadas.txt")