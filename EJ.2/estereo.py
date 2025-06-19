"""
Pol Alaminos Martorell
"""

import struct as st

header_format = "<4sI4s4sIHHIIHH4sI"


def read_wave(file):
    """

    """
    with open(file, "rb") as file_in:

        header = list(st.unpack(header_format, file_in.read(44)))

        data_format = f'<{len(file_in.read()) // 2}h'
        file_in.seek(44)
        
        data = list(st.unpack(data_format, file_in.read()))

    if not (header[0] == b'RIFF' and header[2] == b'WAVE' or header[3] == b'fmt' and header[5] == 1 and header[11] == b'data'):
        raise TypeError("File must be .WAV and have no compresion")

    return data, header


def write_wave(file_out, header, data, mono=True, samples=16):
    """

    """
    header[6] = 1 if mono else 2
    header[12] = len(data) * 2
    header[10] = samples

    header_out = st.pack(header_format, *header)

    data_format = f"<{len(data)}h"
    data_packed = st.pack(data_format, *data)

    with open(file_out, "wb") as file_out:
        file_out.write(header_out)
        file_out.write(data_packed)


def estereo2mono(ficEste, ficMono, canal=2):

    data, header = read_wave(ficEste)

    if not header[6] == 2:
        raise TypeError("File must be stereo")

    if canal == 0:
        mono_data = data[0::2]

    elif canal == 1:
        mono_data = data[1::2]

    elif canal == 2:
        mono_data = [(data[i] + data[i + 1]) //
                     2 for i in range(0, len(data), 2)]

    elif canal == 3:
        mono_data = [(data[i] - data[i + 1]) //
                     2 for i in range(0, len(data), 2)]

    else:
        raise ValueError("Invalid channel, submit 0, 1, 2 or 3.")

    write_wave(ficMono, header, mono_data)


def mono2estereo(ficIzq, ficDer, ficEste):
    """

    """
    data_L, header_L = read_wave(ficIzq)
    data_R, header_R = read_wave(ficDer)

    if not header_L[6] == 1 and header_R[6] == 1:
        raise TypeError("")

    stereo_data = [value for tuple in zip(data_L, data_R) for value in tuple]

    write_wave(ficEste, header_L, stereo_data, mono=False)

    
def codEstereo(ficCod, ficEste):
    data, header = read_wave(ficCod)

    data_L = [(data[i] + data[i+1]) // 2 for i in range(0, len(data), 2)]
    data_R = [(data[i] - data[i+1]) // 2 for i in range(0, len(data), 2)]
    
    data_out = [value for tuple in zip(data_L, data_R) for value in tuple]
    
    write_wave(ficEste, header, data_out, samples=32)

def decEstereo(ficCod, ficEste):
    data, header = read_wave(ficCod)

    data_L = [data[i] + data[i+1] for i in range(0, len(data), 2)]
    data_R = [data[i] - data[i+1] for i in range(0, len(data), 2)]
    
    data_out = [value for tuple in zip(data_L, data_R) for value in tuple]
    
    write_wave(ficEste, header, data_out, mono=False)

if __name__ == '__main__':
    estereo2mono("wav\komm.wav", "wav\komm_Chanel0mono.wav", canal=0)
    estereo2mono("wav\komm.wav", "wav\komm_Chanel1mono.wav", canal=1)
    estereo2mono("wav\komm.wav", "wav\komm_Chanel2mono.wav", canal=2)
    estereo2mono("wav\komm.wav", "wav\komm_Chanel3mono.wav", canal=3)
    
    mono2estereo("wav\komm_Chanel1mono.wav", "wav\komm_Chanel0mono.wav", "wav\komm_stereo.wav")
    
    codEstereo("wav\komm_cod.wav", "wav\komm.wav")
    decEstereo("wav\komm_dec.wav", "wav\komm_cod.wav")