import re

def normalizaHoras(ficText, ficNorm):
    import re

    def formatea(h, m=0):
        return f"{int(h):02}:{int(m):02}"

    def texto_a_hora_min(partes, periodo=None):
        try:
            hora = int(partes[0])
        except ValueError:
            return None

        if 'y cuarto' in partes:
            minuto = 15
        elif 'y media' in partes:
            minuto = 30
        elif 'menos cuarto' in partes:
            hora = hora - 1 if hora > 1 else 12
            minuto = 45
        else:
            minuto = 0

        if hora < 1 or hora > 12:
            return None

        if periodo:
            if periodo == 'de la mañana':
                if hora == 12: hora = 0
            elif periodo == 'del mediodía':
                if hora != 12: hora += 12
            elif periodo == 'de la tarde':
                if 1 <= hora <= 7: hora += 12
                else: return None
            elif periodo == 'de la noche':
                if 8 <= hora <= 11: hora = hora % 12
                elif hora == 12: hora = 0
                elif 1 <= hora <= 4: hora = hora % 12
                else: return None
            elif periodo == 'de la madrugada':
                if 1 <= hora <= 6: hora = hora % 12
                else: return None
        else:
            hora %= 12

        return formatea(hora, minuto)

    patrones = [
        (re.compile(r'\b(\d{1,2})h(\d{1,2})m\b'),
         lambda m: formatea(m[1], m[2]) if m[1].isdigit() and m[2].isdigit() and 0 <= int(m[1]) <= 23 and 0 <= int(m[2]) <= 59 else m[0]),
        (re.compile(r'\b(\d{1,2})h\b'),
         lambda m: formatea(m[1], 0) if m[1].isdigit() and 0 <= int(m[1]) <= 23 else m[0]),
        (re.compile(r'\b(\d{1,2}):(\d{2})\b'),
         lambda m: formatea(m[1], m[2]) if m[1].isdigit() and m[2].isdigit() and 0 <= int(m[1]) <= 23 and 0 <= int(m[2]) <= 59 else m[0]),
        (re.compile(r'\b(\d{1,2}) en punto\b'),
         lambda m: formatea(m[1], 0) if m[1].isdigit() and 0 <= int(m[1]) <= 23 else m[0]),
        (re.compile(r'\b(\d{1,2}) (y cuarto|y media|menos cuarto)? de la (mañana|tarde|noche|madrugada|del mediodía)\b'),
         lambda m: texto_a_hora_min([m[1], m[2]], 'de la ' + m[3]) if m[3] != 'del mediodía' else texto_a_hora_min([m[1], m[2]], m[3])),
        (re.compile(r'\b(\d{1,2}) (y cuarto|y media|menos cuarto)\b'),
         lambda m: texto_a_hora_min([m[1], m[2]])),
    ]

    with open(ficText, encoding='utf-8') as f_in, open(ficNorm, 'w', encoding='utf-8') as f_out:
        for linea in f_in:
            for regex, reemplazo in patrones:
                def reemplazar(match):
                    grupos = match.groups()
                    texto = match.group(0)
                    try:
                        nuevo = reemplazo((texto, *grupos))
                        return nuevo if nuevo else texto
                    except Exception:
                        return texto
                linea = regex.sub(reemplazar, linea)
            f_out.write(linea)
