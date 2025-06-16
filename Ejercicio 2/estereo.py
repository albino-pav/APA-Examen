"""
Nombre y apellido: Joan Gallardo

Este fichero permite manipular ficheros .wav.

Las funciones que incluye son:
- estereo2mono: convierte un fichero .wav estéreo a mono.
- mono2estereo: convierte un fichero .wav mono a estéreo.
- codEstereo: Codifica un fichero de audio estéreo.
- decEstereo: Decodifica un fichero de audio estéreo."""

import struct

def leer_header(f):
    header = f.read(44)
    return header

def escribir_header(f, header):
    f.write(header)

def estereo2mono(ficEste, ficMono, canal=2):
    with open(ficEste, 'rb') as fe:
        header = leer_header(fe)
        data = fe.read()

    muestras = struct.unpack('<' + 'h' * (len(data) // 2), data)
    mono = []

    for i in range(0, len(muestras), 2):
        L = muestras[i]
        R = muestras[i + 1]
        if canal == 0:
            mono.append(L)
        elif canal == 1:
            mono.append(R)
        elif canal == 2:
            mono.append((L + R) // 2)
        elif canal == 3:
            mono.append((L - R) // 2)
        else:
            raise ValueError("Canal no valido")
    
    num_muestras = len(mono)
    subchunk2_size = num_muestras * 2
    chunk_size = 36 + subchunk2_size

    header[22:24] = struct.pack('<H', 1)
    header[32:34] = struct.pack('<H', 2)
    header[34:36] = struct.pack('<H', 16)
    header[40:44] = struct.pack('<I', subchunk2_size)
    header[4:8] = struct.pack('<I', chunk_size)

    with open(ficMono, 'wb') as fm:
        escribir_header(fm, header)
        fm.write(struct.pack('<' + 'h' * num_muestras, *mono))
    
def mono2estereo(ficIzq, ficDer, ficEste):
    with open(ficIzq, 'rb') as fL, open(ficDer, 'rb') as fR:
        headerL = leer_header(fL)
        headerR = leer_header(fR)
        dataL = fL.read()
        dataR = fR.read()

    muestrasL = struct.unpack('<' + 'h' * (len(dataL) // 2), dataL)
    muestrasR = struct.unpack('<' + 'h' * (len(dataR) // 2), dataR)

    if len(muestrasL) != len(muestrasR):
        raise ValueError("Ambos canales deben tener el mismo número de muestras.")

    estereo = []
    for L, R in zip(muestrasL, muestrasR):
        estereo.append(L)
        estereo.append(R)

    num_muestras = len(estereo)
    subchunk2_size = num_muestras * 2
    chunk_size = 36 + subchunk2_size

    headerL[22:24] = struct.pack('<H', 2)
    headerL[32:34] = struct.pack('<H', 4)
    headerL[34:36] = struct.pack('<H', 16)
    headerL[40:44] = struct.pack('<I', subchunk2_size)
    headerL[4:8] = struct.pack('<I', chunk_size)

    with open(ficEste, 'wb') as fe:
        escribir_header(fe, headerL)
        fe.write(struct.pack('<' + 'h' * num_muestras, *estereo))

def codEstereo(ficEste, ficCod):
    with open(ficEste, 'rb') as fe:
        header = leer_header(fe)
        data = fe.read()

    muestras = struct.unpack('<' + 'h' * (len(data) // 2), data)
    codificados = []

    for i in range(0, len(muestras), 2):
        L = muestras[i]
        R = muestras[i + 1]
        suma = (L + R) // 2
        resta = (L - R) // 2
        combinado = ((suma & 0xFFFF) << 16) | (resta & 0xFFFF)
        codificados.append(combinado)

    num_muestras = len(codificados)
    subchunk2_size = num_muestras * 4
    chunk_size = 36 + subchunk2_size

    header[22:24] = struct.pack('<H', 1)
    header[34:36] = struct.pack('<H', 32)
    header[32:34] = struct.pack('<H', 4)
    header[28:32] = struct.pack('<I', struct.unpack('<I', header[28:32])[0] * 2)
    header[40:44] = struct.pack('<I', subchunk2_size)
    header[4:8] = struct.pack('<I', chunk_size)

    with open(ficCod, 'wb') as fc:
        escribir_header(fc, header)
        fc.write(struct.pack('<' + 'I' * num_muestras, *codificados))

def decEstereo(ficCod, ficEste):
    with open(ficCod, 'rb') as fc:
        header = leer_header(fc)
        data = fc.read()

    codificados = struct.unpack('<' + 'I' * (len(data) // 4), data)
    muestras = []

    for c in codificados:
        suma = (c >> 16) & 0xFFFF
        resta = c & 0xFFFF

        if suma >= 0x8000:
            suma -= 0x10000
        if resta >= 0x8000:
            resta -= 0x10000

        L = suma + resta
        R = suma - resta
        muestras.append(L)
        muestras.append(R)

    num_muestras = len(muestras)
    subchunk2_size = num_muestras * 2
    chunk_size = 36 + subchunk2_size

    header[22:24] = struct.pack('<H', 2)
    header[34:36] = struct.pack('<H', 16)
    header[32:34] = struct.pack('<H', 4)
    header[28:32] = struct.pack('<I', struct.unpack('<I', header[28:32])[0] // 2)
    header[40:44] = struct.pack('<I', subchunk2_size)
    header[4:8] = struct.pack('<I', chunk_size)

    with open(ficEste, 'wb') as fe:
        escribir_header(fe, header)
        fe.write(struct.pack('<' + 'h' * num_muestras, *muestras))
