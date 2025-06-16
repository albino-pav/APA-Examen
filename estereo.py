"""
Iker Martínez Rodríguez

En este codigo podemos encontrar diferentes funciones que juegan con los canales de ficheros Wave 
entre las funciones se encuentra la codificación y descodificación de estos últimos.

"""

import struct as st

def estereo2mono(ficEste, ficMono, canal=2):
    """
    La función lee "ficEste" contenedora de una señal estereo y la convierte en "ficMono" 
    una señal monofonica la cual cogerá la señal segun el argumento "canal".
    
    canal = 0 ==> Se almacena en el canal izquierdo (L).
    canal = 1 ==> Se almacena en el canal derecho (R).
    canal = 2 ==> Se almacena la semisuma (L+R)/2. (Default)
    canal = 3 ==> Se almacena la semidiferencia (L-R)/2.
    """

    with open(ficEste, 'rb') as fpEstero:
        formato = '<4sI4s4sIHHIIH4sI'
        datos = ficEste.read(st.calcsize(formato))
        headerData = list(st.unpack(formato, datos))
        # chunkID[0], chunkSize[1], format[2], chunk1ID[3], chunk1Size[4], audFormat[5], nChannels[6], sampleRate[7], bitRate[8], bAlign[9], bps[10], chunk2ID[11], fileSize[12]  
        
        if headerData[0] != b'RIFF' or headerData[2] != b'WAVE':
            raise Exception(f'El fichero {ficEste} no tiene formato WAVE.')
        
        with open(ficMono, 'wb') as fpMono:
            fpEstero.seek(44, 0) # Posicionamos el puntero de lectura al principio de los datos (byte 44)
            for i in range(0, headerData[12]):
                L = fpEstero.read(2)
                R = fpEstero.read(2)
            
            # Cambiamos el numero de canales en la cabecera
            headerData[6] = 1
            fpMono.write(headerData)

            if canal == 0:
                fpMono.write(L)

            elif canal == 1:
                fpMono.write(R)
                
            elif canal == 2:
                mono = (L+R)/2 
                fpMono.write(mono)
                
            elif canal == 3:
                mono = (L-R)/2
                fpMono.write(mono)

def mono2estereo(ficIzq, ficDer, ficEste):
    """
    A partir de las dos señales monofonicas dadas ("ficIzq","ficDer") se construye una
    señal estereo ("ficEste").
    """

    with open(ficIzq, 'rb') as fpIzq:
        formato = '<4sI4s4sIHHIIH4sI'
        datos = ficEste.read(st.calcsize(formato))
        headerDataL = list(st.unpack(formato, datos))

        with open(ficDer, 'rb') as fpDer:
            formato = '<4sI4s4sIHHIIH4sI'
            datos = ficEste.read(st.calcsize(formato))
            headerDataR = list(st.unpack(formato, datos)) 

            # Comprovamos coincidencias por orden: RIFF, sampleRate, fileSize
            if headerDataL[0] != b'RIFF' or headerDataR[0] != b'RIFF':
                raise Exception(f'Los ficheros de entrada no tienen formato WAVE.')
            if headerDataL[7] != headerDataR[7]:
                raise Exception(f'La frequencia de muestro de los ficheros no coincide.')
            if headerDataL[12] != headerDataR[12]:
                raise Exception(f'El tamaño de los ficheros no coincide.')

            with open(ficEste, 'wb') as fpEste:
                # Cambiamos el numero de canales a 2 y añadimos la cabecera al fichero de salida
                headerDataL[6] = 2 
                fpEste.write(headerDataL)

                for i in range(0, len(fpDer)):
                    L = fpIzq.read(2)
                    R = fpDer.read(2)
                    fpEste.write(L)
                    fpEste.write(R)

def codEstereo(ficEste, ficCod):
    """
    Esta función toma como entrada una señal estéreo almacenada en "ficEste" con codificación 
    PCM lineal de 16 bits, y genera una nueva señal en formato de 32 bits. El objetivo es 
    asegurar su compatibilidad con sistemas de reproducción monofónicos, así como con equipos
    estéreo que admitan este tipo de codificación.
    """
    
    with open(ficEste, 'rb') as fpEste:
        # leemos la cabecera
        formato = '<4sI4s4sIHHIIH4sI'
        datos = ficEste.read(st.calcsize(formato))
        headerData = list(st.unpack(formato, datos))

        if headerData[0] != b'RIFF' or headerData[2] != b'WAVE':
            raise Exception(f'El fichero {ficEste} no tiene formato WAVE.')

        for i in range(0, headerData[12]):
                L = fpEste.read(2)
                R = fpEste.read(2)

        semiSum = (L+R)/2
        semiDif = (L-R)/2

        with open(ficCod, 'wb') as fpCod:
            for i in range(0, len(semiSum), 2):
                fpCod.write(semiSum[i], semiSum[i+1])
                fpCod.write(semiDif[i], semiDif[i+1])

def decEstereo(ficCod, ficEste):
    """
    A partir de "ficCod" (una señal monofonica de 32 bits) se generará la señal "ficEste" que 
    contendrá la semisuma de los canales L y R, creada a partir de los 16 MSB de la señal 
    original, y la semidiferencia de estos, a partir de los 16 LSB. Los dos canales por
    separado en formato Wave estereo.
    """
    
    with open(ficCod, 'rb') as fpCod:
        # leemos la cabecera
        formato = '<4sI4s4sIHHIIH4sI'
        datos = ficEste.read(st.calcsize(formato))
        headerData = list(st.unpack(formato, datos))

        if headerData[0] != b'RIFF' or headerData[2] != b'WAVE':
            raise Exception(f'El fichero {ficEste} no tiene formato WAVE.')
        
        for i in range(0, headerData[12]):
            semiSum = fpCod.read(2)
            semiDif = fpCod.read(2)
        
        for i in range(0, len(semiSum)):
            R = -(4 * semiDif[i] - 4 * semiSum[i]) / 3
            L = 2 * semiSum[i] + 2 * (semiDif[i] - semiSum[i]) / 3

        with open(ficEste, 'wb') as fpEste:
            for i in range(0, len(semiSum), 2):
                fpEste.write(L[i], L[i+1])
                fpEste.write(R[i], R[i+1])