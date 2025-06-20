"""
Autor: Pau reyes Boix

Utilitats per al processament de fitxers WAVE PCM sense compressió.

Funcionalitats:
- Conversió d'estèreo a mono amb diferents mètodes
- Generació d'estèreo a partir de canals mono
- Codificació d'àudio estèreo en format compacte de 32 bits
- Decodificació inversa a dos canals de 16 bits

"""

import struct

def llegir_capcalera(f):
    """
    Llegeix la capçalera d'un fitxer WAVE PCM.

    Paràmetres:
    - f: fitxer obert en mode binari ('rb')

    Retorna:
    - Diccionari amb les propietats: canals, freq, bits i mida de dades.
    """
    if f.read(4) != b'RIFF':
        raise ValueError("No és un fitxer RIFF")
    _ = f.read(4)  # mida total, ignorada
    if f.read(4) != b'WAVE':
        raise ValueError("No és un fitxer WAVE")

    if f.read(4) != b'fmt ':
        raise ValueError("No s'ha trobat el bloc 'fmt '")
    if struct.unpack('<I', f.read(4))[0] != 16:
        raise ValueError("Només s'accepta format PCM")

    fmt = struct.unpack('<HHIIHH', f.read(16))
    canals, freq, bits = fmt[1], fmt[2], fmt[5]

    if f.read(4) != b'data':
        raise ValueError("No s'ha trobat el bloc de dades")
    mida_dades = struct.unpack('<I', f.read(4))[0]

    return {
        'canals': canals,
        'freq': freq,
        'bits': bits,
        'data_mida': mida_dades
    }

def escriure_capcalera(f, canals, freq, bits, mida_dades):
    """
    Escriu una capçalera WAVE PCM bàsica.

    Paràmetres:
    - f: fitxer obert en mode escriptura binària ('wb')
    - canals: nombre de canals (1 mono, 2 estèreo)
    - freq: freqüència de mostreig en Hz
    - bits: bits per mostra (16 o 32)
    - mida_dades: mida de les dades d'àudio en bytes
    """
    byte_rate = freq * canals * bits // 8
    bloc_align = canals * bits // 8
    mida_total = 36 + mida_dades

    f.write(b'RIFF')
    f.write(struct.pack('<I', mida_total))
    f.write(b'WAVE')
    f.write(b'fmt ')
    f.write(struct.pack('<IHHIIHH', 16, 1, canals, freq, byte_rate, bloc_align, bits))
    f.write(b'data')
    f.write(struct.pack('<I', mida_dades))

def reduir_mostra(mostra, bytes_per_canal, mode):
    """
    Processa una mostra estèreo i retorna la conversió mono segons mode.

    Modes possibles:
    - 0: canal esquerre
    - 1: canal dret
    - 2: mitjana (L + R) // 2
    - 3: diferència (L - R) // 2

    Paràmetres:
    - mostra: bytes de la mostra (2 canals)
    - bytes_per_canal: bytes per canal (normalment 2)
    - mode: tipus de conversió

    Retorna:
    - Bytes de la mostra mono processada.
    """
    L = int.from_bytes(mostra[:bytes_per_canal], 'little', signed=True)
    R = int.from_bytes(mostra[bytes_per_canal:], 'little', signed=True)

    if mode == 0:
        val = L
    elif mode == 1:
        val = R
    elif mode == 2:
        val = (L + R) // 2
    elif mode == 3:
        val = (L - R) // 2
    else:
        raise ValueError("Mode de conversió desconegut")

    return val.to_bytes(bytes_per_canal, 'little', signed=True)

def convertir_estereo_a_mono(fitxer_in, fitxer_out, mode=2):
    """
    Converteix un fitxer estèreo de 16 bits a mono segons mode triat.

    Paràmetres:
    - fitxer_in: ruta del fitxer estèreo original
    - fitxer_out: ruta del fitxer mono resultant
    - mode: tipus de conversió (0,1,2,3)
    """
    with open(fitxer_in, 'rb') as f:
        cap = llegir_capcalera(f)
        if cap['canals'] != 2 or cap['bits'] != 16:
            raise ValueError("Només s'accepten fitxers estèreo de 16 bits")
        dades = f.read(cap['data_mida'])

    tam = cap['bits'] // 8
    result = bytearray()

    for i in range(0, len(dades), 2 * tam):
        mostra = dades[i:i + 2 * tam]
        result.extend(reduir_mostra(mostra, tam, mode))

    with open(fitxer_out, 'wb') as f_out:
        escriure_capcalera(f_out, 1, cap['freq'], cap['bits'], len(result))
        f_out.write(result)

def combinar_mono_en_estereo(fitxer_L, fitxer_R, fitxer_out):
    """
    Combina dos fitxers mono en un estèreo.

    Paràmetres:
    - fitxer_L: fitxer mono canal esquerre
    - fitxer_R: fitxer mono canal dret
    - fitxer_out: fitxer estèreo resultant
    """
    with open(fitxer_L, 'rb') as fL, open(fitxer_R, 'rb') as fR:
        cap_L = llegir_capcalera(fL)
        cap_R = llegir_capcalera(fR)

        if cap_L != cap_R:
            raise ValueError("Els dos fitxers mono han de tenir el mateix format")

        dades_L = fL.read(cap_L['data_mida'])
        dades_R = fR.read(cap_R['data_mida'])

    tam = cap_L['bits'] // 8
    mostres = bytearray()

    for i in range(0, len(dades_L), tam):
        mostres.extend(dades_L[i:i+tam] + dades_R[i:i+tam])

    with open(fitxer_out, 'wb') as f:
        escriure_capcalera(f, 2, cap_L['freq'], cap_L['bits'], len(mostres))
        f.write(mostres)

def codificar_estereo_32bit(fitxer_estereo, fitxer_codificat):
    """
    Codifica un fitxer estèreo de 16 bits a mono de 32 bits amb semisuma i semidiferència.

    Paràmetres:
    - fitxer_estereo: fitxer d'entrada estèreo 16 bits
    - fitxer_codificat: fitxer mono 32 bits resultant
    """
    with open(fitxer_estereo, 'rb') as f:
        cap = llegir_capcalera(f)
        if cap['canals'] != 2 or cap['bits'] != 16:
            raise ValueError("El fitxer ha de ser estèreo de 16 bits")
        dades = f.read(cap['data_mida'])

    mostres = [struct.unpack('<hh', dades[i:i+4]) for i in range(0, len(dades), 4)]
    codificades = bytearray()

    for L, R in mostres:
        S = (L + R) // 2
        D = (L - R) // 2
        val = ((S & 0xFFFF) << 16) | (D & 0xFFFF)
        codificades.extend(struct.pack('<I', val))

    with open(fitxer_codificat, 'wb') as f_out:
        escriure_capcalera(f_out, 1, cap['freq'], 32, len(codificades))
        f_out.write(codificades)

def a_signed_16(val):
    """
    Converteix un valor de 16 bits sense signe a signat (conversió complement a 2).
    """
    return val if val < 0x8000 else val - 0x10000

def saturar_16bit(val):
    """
    Saturació per mantenir el valor dins el rang de 16 bits signats.
    """
    return max(-32768, min(32767, val))

def descodificar_estereo_32bit(fitxer_codificat, fitxer_estereo):
    """
    Descodifica un fitxer mono 32 bits en un fitxer estèreo 16 bits original.

    Paràmetres:
    - fitxer_codificat: fitxer mono 32 bits codificat
    - fitxer_estereo: fitxer estèreo 16 bits resultant
    """
    with open(fitxer_codificat, 'rb') as f:
        cap = llegir_capcalera(f)
        if cap['canals'] != 1 or cap['bits'] != 32:
            raise ValueError("Fitxer no vàlid per descodificar")
        dades = f.read(cap['data_mida'])

    blocs = [struct.unpack('<I', dades[i:i+4])[0] for i in range(0, len(dades), 4)]
    mostres = []

    for b in blocs:
        S = b >> 16
        D = a_signed_16(b & 0xFFFF)
        L = saturar_16bit(S + D)
        R = saturar_16bit(S - D)
        mostres.append(struct.pack('<hh', L, R))

    with open(fitxer_estereo, 'wb') as f_out:
        escriure_capcalera(f_out, 2, cap['freq'], 16, len(mostres) * 4)
        f_out.write(b''.join(mostres))
