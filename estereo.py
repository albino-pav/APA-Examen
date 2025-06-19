import struct

def leer_cabecera_wav(fichero):
    with open(fichero, 'rb') as f:
        cabecera = f.read(44)
        if cabecera[:4] != b'RIFF' or cabecera[8:12] != b'WAVE':
            raise ValueError("No es un archivo WAVE válido.")
        return cabecera

def escribir_cabecera_wav(fichero, cabecera):
    with open(fichero, 'wb') as f:
        f.write(cabecera)

def estereo2mono(ficEste, ficMono, canal=2):
    cabecera = leer_cabecera_wav(ficEste)
    with open(ficEste, 'rb') as f:
        f.seek(44)
        datos = f.read()
    
    muestras = []
    if canal == 0:
        muestras = [struct.unpack('<h', datos[i:i+2])[0] for i in range(0, len(datos), 4)]
    elif canal == 1:
        muestras = [struct.unpack('<h', datos[i+2:i+4])[0] for i in range(0, len(datos), 4)]
    elif canal == 2:
        muestras = [((struct.unpack('<h', datos[i:i+2])[0] + struct.unpack('<h', datos[i+2:i+4])[0]) // 2) for i in range(0, len(datos), 4)]
    elif canal == 3:
        muestras = [((struct.unpack('<h', datos[i:i+2])[0] - struct.unpack('<h', datos[i+2:i+4])[0]) // 2) for i in range(0, len(datos), 4)]
    else:
        raise ValueError("El parámetro 'canal' debe ser 0, 1, 2 o 3.")
    
    muestras_bytes = b''.join(struct.pack('<h', m) for m in muestras)
    
    # Modificar cabecera para indicar nuevo tamaño de datos
    tamaño_datos = len(muestras_bytes)
    cabecera_mod = bytearray(cabecera)
    cabecera_mod[4:8] = struct.pack('<I', 36 + tamaño_datos)  # Tamaño total - 8 bytes
    cabecera_mod[40:44] = struct.pack('<I', tamaño_datos)
    
    with open(ficMono, 'wb') as out_f:
        out_f.write(cabecera_mod)
        out_f.write(muestras_bytes)

def mono2estereo(ficIzq, ficDer, ficEste):
    cabecera_izq = leer_cabecera_wav(ficIzq)
    cabecera_der = leer_cabecera_wav(ficDer)
    if cabecera_izq != cabecera_der:
        raise ValueError("Cabeceras de los ficheros monofónicos no coinciden.")
    
    with open(ficIzq, 'rb') as f:
        f.seek(44)
        datos_izq = f.read()
    with open(ficDer, 'rb') as f:
        f.seek(44)
        datos_der = f.read()
    
    if len(datos_izq) != len(datos_der):
        raise ValueError("Los ficheros monofónicos no tienen la misma longitud.")
    
    muestras = b''.join(
        struct.pack('<hh',
                    struct.unpack('<h', datos_izq[i:i+2])[0],
                    struct.unpack('<h', datos_der[i:i+2])[0])
        for i in range(0, len(datos_izq), 2)
    )

    tamaño_datos = len(muestras)
    cabecera_mod = bytearray(cabecera_izq)
    cabecera_mod[4:8] = struct.pack('<I', 36 + tamaño_datos)
    cabecera_mod[40:44] = struct.pack('<I', tamaño_datos)
    
    with open(ficEste, 'wb') as f:
        f.write(cabecera_mod)
        f.write(muestras)

def codEstereo(ficEste, ficCod):
    cabecera = leer_cabecera_wav(ficEste)
    with open(ficEste, 'rb') as f:
        f.seek(44)
        datos = f.read()
    muestras_codificadas = []
    for i in range(0, len(datos), 4):
        L = struct.unpack('<h', datos[i:i+2])[0]
        R = struct.unpack('<h', datos[i+2:i+4])[0]
        semisuma = (L + R) // 2
        semidif = (L - R) // 2
        valor = ((semisuma & 0xFFFF) << 16) | (semidif & 0xFFFF)
        muestras_codificadas.append(valor)
    muestras_bytes = b''.join(struct.pack('<I', m) for m in muestras_codificadas)
    
    tamaño_datos = len(muestras_bytes)
    cabecera_mod = bytearray(cabecera)
    cabecera_mod[4:8] = struct.pack('<I', 36 + tamaño_datos)
    # Cambiar el formato en cabecera a 32 bits (bitsPerSample)
    # bitsPerSample en byte 34 (offset 34) y 35 (offset 35) en cabecera RIFF
    cabecera_mod[34:36] = struct.pack('<H', 32)
    # Ajustar numChannels a 1 pues ahora es mono de 32 bits
    cabecera_mod[22:24] = struct.pack('<H', 1)
    cabecera_mod[40:44] = struct.pack('<I', tamaño_datos)
    
    with open(ficCod, 'wb') as f:
        f.write(cabecera_mod)
        f.write(muestras_bytes)

def decEstereo(ficCod, ficEste):
    cabecera = leer_cabecera_wav(ficCod)
    with open(ficCod, 'rb') as f:
        f.seek(44)
        datos = f.read()
    muestras_izq = []
    muestras_der = []
    for i in range(0, len(datos), 4):
        valor = struct.unpack('<I', datos[i:i+4])[0]
        semisuma = (valor >> 16) & 0xFFFF
        semidif = valor & 0xFFFF
        # Convertir a signed 16-bit
        if semisuma >= 0x8000:
            semisuma -= 0x10000
        if semidif >= 0x8000:
            semidif -= 0x10000
        L = semisuma + semidif
        R = semisuma - semidif
        muestras_izq.append(L)
        muestras_der.append(R)
    muestras_bytes = b''.join(
        struct.pack('<hh', l, r) for l, r in zip(muestras_izq, muestras_der)
    )
    
    tamaño_datos = len(muestras_bytes)
    cabecera_mod = bytearray(cabecera)
    cabecera_mod[4:8] = struct.pack('<I', 36 + tamaño_datos)
    # bitsPerSample a 16 para mono estereo
    cabecera_mod[34:36] = struct.pack('<H', 16)
    cabecera_mod[22:24] = struct.pack('<H', 2)  # 2 canales
    cabecera_mod[40:44] = struct.pack('<I', tamaño_datos)
    
    with open(ficEste, 'wb') as f:
        f.write(cabecera_mod)
        f.write(muestras_bytes)

