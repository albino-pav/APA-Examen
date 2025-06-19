
"""
Nombre : Montserrat Cuevas López

Este fichero contiene funciones para manejar señales estéreo de un fichero
WAVE de 16 bits.
Incluye funciones para convertir de mono a estéreo, de estéreo a mono y 
codificar y decodificar señales estéreo usando los bits menos significativos.

"""

import struct

def empaquetar_cabecera(num_channels, sample_rate, bits_sample, data_size):

    """
    Empaqueta una cabecera WAVE a partir de los parámetros dados.
    Devuelve los bytes de la cabecera completa.
    """
    byte_rate = sample_rate * num_channels * bits_sample // 8
    block_align =num_channels * bits_sample // 8
    riff_size = 36 + data_size # 36 = 12 bytres del RIFF + 24 del FMT
    return (
        struct.pack('4sI4s', b'RIFF', riff_size, b'WAVE') +
        struct.pack('<4sIHHIIHH', b'fmt ', 16, 1, num_channels, 
                    sample_rate, byte_rate, block_align, bits_sample) +
        struct.pack('<4sI', b'data', data_size )
    )

def desempaquetar_cabecera(f):
    """
    Lee y desempaquera la cabecera de un fichero.
    Devuelve un diccionario con los datos del audio.
    """
    f.seek(0)
    riff, _, wave = struct.unpack('<4sI4s', f.read(12))
    if riff != b'RIFF' or wave != b'WAVE':
        raise TypeError('No es un fichero WAVE')
    data_offset = None
    data_size = None
    audio_format = None
    num_channels = None
    sample_rate = None
    bits_sample = None
    while True:
        cabecera = f.read(8)
        if len(cabecera) < 8:
            break
        chunk_id, chunk_size = struct.unpack('<4sI', cabecera)
        if chunk_id == b'fmt ':
            fmt_data = f.read(chunk_size)
            audio_format, num_channels, sample_rate, byte_rate, block_align, bits_sample = struct.unpack('<HHIIHH', fmt_data[:16])
        elif chunk_id == b'data':
            data_offset = f.tell()
            data_size= chunk_size
            f.seek(chunk_size, 1)
        else:
            f.seek(chunk_size, 1)
    if audio_format != 1 or bits_sample not in (16, 32):
        raise TypeError("Formato no soportado, no es PCM lineal de 16 bits")
    return {
        'num_channels': num_channels,
        'sample_rate': sample_rate,
        'bits_sample': bits_sample,
        'data_offset': data_offset,
        'data_size': data_size
    }

 
def estereo2mono(ficEste, ficMono, canal=2):
    '''
    Convierte un archivo (ficEste) de estéreo a mono, el fichero mono resultante
    dependerá del argumento canal; 0 para canal izquierdo, 1 para canal derecho,
    2 para la semisuma y 3 para la semidiferencia.
    '''
    with open(ficEste, 'rb') as fpEstereo:
        info = desempaquetar_cabecera(fpEstereo)
        if info ['num_channels'] != 2:
            raise TypeError("El fichero no es estéreo")
        fpEstereo.seek(info['data_offset'])
        datos = fpEstereo.read(info['data_size'])

    muestras = struct.unpack('<' + 'h' * (info['data_size'] // 2), datos)
    pares = zip(muestras[::2], muestras[1::2]) #izquierda, derecha

    if canal == 0:
        salida = [l for l, r in pares]
    elif canal ==1:
        salida = [r for l, r in pares]
    elif canal == 2:
        salida = [((l+r) // 2) for l, r in pares]
    elif canal == 3:
        salida = [((l-r) // 2) for l, r in pares]
    else:
        raise TypeError('canal no válido')
    
    datos_mono = struct.pack('<' + 'h' * len(salida), *salida)

    with open(ficMono, 'wb') as f:
        f.write(empaquetar_cabecera(1, info['sample_rate'], 16, len(datos_mono)))
        f.write(datos_mono)

def mono2estereo(ficIzq, ficDer, ficEste):
    '''
    A partir de dos ficheros mono, uno que corresponde al canal izquierdo y otro al derecho, 
    crea un archivo estéreo
    '''
    with open(ficIzq, 'rb') as fpIzq:
        info_izq = desempaquetar_cabecera(fpIzq)
        if info_izq['num_channels'] !=1:
            raise TypeError("El fichero no es mono")
        fpIzq.seek(info_izq['data_offset'])
        datos_izq = struct.unpack('<' + 'h' * (info_izq['data_size'] // 2), fpIzq.read(info_izq['data_size']))
    
    with open(ficDer, 'rb') as fpDer:
        info_der = desempaquetar_cabecera(fpDer)
        if info_der['num_channels'] != 1:
            raise TypeError("El fichero no es mono")
        fpDer.seek(info_der['data_offset'])
        datos_der = struct.unpack('<' + 'h' * (info_der['data_size'] // 2), fpDer.read(info_izq['data_size']))

    datos_estereo = struct.pack('<' + 'h' * (2 * len(datos_izq)),
                                *sum(zip(datos_izq, datos_der), ()))
    with open(ficEste, 'wb') as fpEste:
        fpEste.write(empaquetar_cabecera(2, info_izq['sample_rate'], 16, len(datos_estereo)))
        fpEste.write(datos_estereo)

def codEstereo(ficEste, ficCod):
    '''
    Lee el fichero ficEste, que contiene una señal estéreo codificada con PCM lineal de 16 bits,
    y construye con ellas una señal codificada con 32 bits que permita su reproducción
    tanto por sistemas monofónicos como por sistemas estéreo preparados para ello
    '''
    with open(ficEste, 'rb') as fp:
        info = desempaquetar_cabecera(fp)
        if info['num_channels'] != 2:
            raise TypeError("El fichero no es estéreo")
        fp.seek(info['data_offset'])
        datos = struct.unpack('<' + 'h' * (info['data_size'] // 2), fp.read(info['data_size']))

    pares = zip(datos[::2], datos[1::2])
    codificados = [((l + r) << 16) & 0xFFFF0000 | ((l - r) & 0xFFFF) for l, r in pares]

    datos_cod = struct.pack('<' + 'I' * len(codificados), *codificados)

    with open(ficCod, 'wb') as fpDos:
        fpDos.write(empaquetar_cabecera(1, info['sample_rate'], 32, len(datos_cod)))
        fpDos.write(datos_cod)

def decEstereo(ficCod, ficEste):
    '''
    Lee el fichero ficCod con una señal monofónica de 32 bits en la que 
    los 16 bits más significativos contienen la semisuma de los 
    dos canales de una señal estéreo y los 16 bits menos significativos la semidiferencia,
    y escribe el fichero ficEste con los dos canales por separado en el formato de los ficheros WAVE estéreo
    '''
    with open(ficCod, 'rb') as fpCod:
        info = desempaquetar_cabecera(fpCod)
        if info['bits_sample'] != 32:
            raise TypeError('El fichero no está codificado en 32 bits')
        fpCod.seek(info['data_offset'])
        datos = struct.unpack('<' + 'I' * (info['data_size'] // 4), fpCod.read(info['data_size']))

        reconstruidos = []

        for cod in datos:
            suma = (cod >> 16) & 0xFFFF
            diff_raw = cod & 0xFFFF
            # diff y suma como entero con signo 16 bit
            suma = struct.unpack('<h', struct.pack('<H', diff_raw))[0]
            diff = struct.unpack('<h', struct.pack('<H', diff_raw))[0]
            izq = (suma + diff) // 2
            der = (suma - diff) // 2
            #reconstruir los canales
            reconstruidos.append(int(izq)) 
            reconstruidos.append(int(der)) 

    datos_estereo = struct.pack('<' + 'h' * len(reconstruidos), *reconstruidos)

    with open(ficEste, 'wb') as fpEste:
         fpEste.write(empaquetar_cabecera(2, info['sample_rate'], 16, len(datos_estereo)))
         fpEste.write(datos_estereo)



