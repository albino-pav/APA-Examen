# mismo archivo que el que hice para APA-T6

import re

def normalizaHoras(ficText, ficNorm):
    patrones = [
        # 1. HH:MM
        (re.compile(r'\b(\d{1,2}):(\d{2})\b'),
         lambda m: f"{int(m.group(1)):02}:{int(m.group(2)):02}"
         if 0 <= int(m.group(1)) < 24 and 0 <= int(m.group(2)) < 60 else m.group(0)),

        # 2. HHhMMm
        (re.compile(r'\b(\d{1,2})h(\d{1,2})m\b'),
         lambda m: f"{int(m.group(1)):02}:{int(m.group(2)):02}"
         if 0 <= int(m.group(1)) < 24 and 0 <= int(m.group(2)) < 60 else m.group(0)),

        # 3. HHh
        (re.compile(r'\b(\d{1,2})h\b'),
         lambda m: f"{int(m.group(1)):02}:00"
         if 0 <= int(m.group(1)) < 24 else m.group(0)),

        # 4. 'HHh de la mañana' o 'HHh de la tarde'
        (re.compile(r'\b(\d{1,2})h de la (mañana|tarde)\b'),
         lambda m: f"{(int(m.group(1)) % 12 + (12 if m.group(2) == 'tarde' else 0)):02}:00"
         if 1 <= int(m.group(1)) <= 12 else m.group(0)),

        # 5. 'HH y media de la tarde' o mañana
        (re.compile(r'\b(\d{1,2}) y media(?: de la (mañana|tarde))?\b'),
         lambda m: f"{(int(m.group(1)) % 12 + (12 if m.group(2) == 'tarde' else 0)):02}:30"),

        # 6. 'HH y cuarto de la mañana/tarde'
        (re.compile(r'\b(\d{1,2}) y cuarto(?: de la (mañana|tarde))?\b'),
         lambda m: f"{(int(m.group(1)) % 12 + (12 if m.group(2) == 'tarde' else 0)):02}:15"),

        # 7. 'HH menos cuarto de la mañana/tarde'
        (re.compile(r'\b(\d{1,2}) menos cuarto(?: de la (mañana|tarde))?\b'),
         lambda m: f"{((int(m.group(1)) - 1) % 12 + (12 if m.group(2) == 'tarde' else 0)):02}:45"),

        # 8. 'HH en punto de la mañana/tarde'
        (re.compile(r'\b(\d{1,2}) en punto(?: de la (mañana|tarde))?\b'),
         lambda m: f"{(int(m.group(1)) % 12 + (12 if m.group(2) == 'tarde' else 0)):02}:00"),

        # 9. '12 de la noche'
        (re.compile(r'\b12 de la noche\b'),
         lambda m: '00:00'),
    ]

    with open(ficText, 'r', encoding='utf-8') as fin, open(ficNorm, 'w', encoding='utf-8') as fout:
        for linea in fin:
            nueva_linea = linea
            for patron, funcion in patrones:
                try:
                    nueva_linea = patron.sub(lambda m: funcion(m), nueva_linea)
                except Exception:
                    continue
            fout.write(nueva_linea)

if __name__ == "__main__":
    normalizaHoras("horas.txt", "horas_normalizadas.txt")

