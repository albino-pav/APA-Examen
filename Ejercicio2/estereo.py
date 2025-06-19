"""
Name and Surname: Marti Dominguez

Description:
This module handles the conversion between stereo and mono signals, as well as
the encoding and decoding of stereo signals using 32-bit integers.
It includes the functions:
  - estereo2mono(ficEste, ficMono, canal=2)
  - mono2estereo(ficIzq, ficDer, ficEste)
  - codEstereo(ficEste, ficCod)
  - decEstereo(ficCod, ficEste)
"""

import struct

# WAV header format (44 bytes)
WAV_HEADER_FORMAT = '<4sI4s4sIHHIIHH4sI'
HEADER_SIZE = 44

def read_wav_header(f):
    header = f.read(HEADER_SIZE)
    if len(header) != HEADER_SIZE:
        raise ValueError("Incomplete header")
    header_tuple = struct.unpack(WAV_HEADER_FORMAT, header)
    # Verify that the file is a WAVE file
    if header_tuple[0] != b'RIFF' or header_tuple[2] != b'WAVE':
        raise ValueError("The file is not a valid WAVE file")
    return header_tuple

def write_wav_header(f, chunk_size, subchunk2_size, num_channels, sample_rate, bits_per_sample):
    block_align = num_channels * (bits_per_sample // 8)
    byte_rate = sample_rate * block_align
    header = struct.pack(WAV_HEADER_FORMAT,
                         b'RIFF',
                         chunk_size,
                         b'WAVE',
                         b'fmt ',
                         16,  # SubChunk1Size for PCM
                         1,   # AudioFormat (PCM)
                         num_channels,
                         sample_rate,
                         byte_rate,
                         block_align,
                         bits_per_sample,
                         b'data',
                         subchunk2_size)
    f.write(header)

def estereo2mono(ficEste, ficMono, canal=2):
    # Open the input file for reading
    infile = open(ficEste, 'rb')
    header = read_wav_header(infile)
    num_channels = header[6]
    bits_per_sample = header[10]
    if num_channels != 2 or bits_per_sample != 16:
        infile.close()
        raise ValueError("The input file must be 16-bit stereo")
    subchunk2_size = header[12]
    frame_size = num_channels * (bits_per_sample // 8)
    n_frames = subchunk2_size // frame_size
    data = infile.read(subchunk2_size)
    infile.close()
    
    # Manually extract left and right samples
    stereo_samples = struct.unpack('<' + 'h' * (n_frames * 2), data)
    left = []
    right = []
    for i in range(n_frames):
        left.append(stereo_samples[2*i])
        right.append(stereo_samples[2*i+1])
    
    # Determine the output channel
    mono_samples = []
    if canal == 0:
        mono_samples = left
    elif canal == 1:
        mono_samples = right
    elif canal == 2:
        # Half-sum of L and R
        for i in range(n_frames):
            mono_samples.append((left[i] + right[i]) // 2)
    elif canal == 3:
        # Half-difference of L and R
        for i in range(n_frames):
            mono_samples.append((left[i] - right[i]) // 2)
    else:
        raise ValueError("Incorrect channel value")
    
    # Prepare the new header for the mono file
    new_num_channels = 1
    new_block_align = new_num_channels * (bits_per_sample // 8)
    new_subchunk2_size = n_frames * new_block_align
    new_chunk_size = 36 + new_subchunk2_size
    mono_data = struct.pack('<' + 'h' * n_frames, *mono_samples)
    
    outfile = open(ficMono, 'wb')
    write_wav_header(outfile, new_chunk_size, new_subchunk2_size, new_num_channels, header[7], bits_per_sample)
    outfile.write(mono_data)
    outfile.close()

def mono2estereo(ficIzq, ficDer, ficEste):
    # Read the left file
    f_izq = open(ficIzq, 'rb')
    header_izq = read_wav_header(f_izq)
    if header_izq[6] != 1 or header_izq[10] != 16:
        f_izq.close()
        raise ValueError("The left file must be 16-bit mono")
    subchunk2_size_izq = header_izq[12]
    n_frames = subchunk2_size_izq // (header_izq[10] // 8)
    data_izq = f_izq.read(subchunk2_size_izq)
    f_izq.close()
    
    # Read the right file
    f_der = open(ficDer, 'rb')
    header_der = read_wav_header(f_der)
    if header_der[6] != 1 or header_der[10] != 16:
        f_der.close()
        raise ValueError("The right file must be 16-bit mono")
    subchunk2_size_der = header_der[12]
    n_frames_der = subchunk2_size_der // (header_der[10] // 8)
    if n_frames_der != n_frames:
        f_der.close()
        raise ValueError("Mono files have a different number of samples")
    data_der = f_der.read(subchunk2_size_der)
    f_der.close()
    
    # Extract individual samples with a simple loop
    samples_izq = list(struct.unpack('<' + 'h' * n_frames, data_izq))
    samples_der = list(struct.unpack('<' + 'h' * n_frames, data_der))
    
    # Combine the samples of both channels in an alternating fashion
    stereo_samples = []
    for i in range(n_frames):
        stereo_samples.append(samples_izq[i])
        stereo_samples.append(samples_der[i])
    
    new_num_channels = 2
    bits = header_izq[10]  # 16 bits
    new_block_align = new_num_channels * (bits // 8)
    new_subchunk2_size = n_frames * new_block_align
    new_chunk_size = 36 + new_subchunk2_size
    stereo_data = struct.pack('<' + 'h' * (n_frames * 2), *stereo_samples)
    
    f_out = open(ficEste, 'wb')
    write_wav_header(f_out, new_chunk_size, new_subchunk2_size, new_num_channels, header_izq[7], bits)
    f_out.write(stereo_data)
    f_out.close()

def codEstereo(ficEste, ficCod):
    f_in = open(ficEste, 'rb')
    header = read_wav_header(f_in)
    if header[6] != 2 or header[10] != 16:
        f_in.close()
        raise ValueError("The input file must be 16-bit stereo")
    subchunk2_size = header[12]
    frame_size = 2 * (header[10] // 8)
    n_frames = subchunk2_size // frame_size
    data = f_in.read(subchunk2_size)
    f_in.close()
    
    stereo_samples = struct.unpack('<' + 'h' * (n_frames * 2), data)
    
    left = []
    right = []
    for i in range(n_frames):
        left.append(stereo_samples[2*i])
        right.append(stereo_samples[2*i+1])
    
    codes = []
    for i in range(n_frames):
        # Calculate half-sum and half-difference
        s = (left[i] + right[i]) // 2
        d = (left[i] - right[i]) // 2
        # Combine into 32 bits (not very optimized, but okay)
        code = (s << 16) | (d & 0xFFFF)
        codes.append(code)
    
    new_num_channels = 1
    bits = 32
    new_block_align = new_num_channels * (bits // 8)
    new_subchunk2_size = n_frames * new_block_align
    new_chunk_size = 36 + new_subchunk2_size
    cod_data = struct.pack('<' + 'i' * n_frames, *codes)
    
    f_out = open(ficCod, 'wb')
    write_wav_header(f_out, new_chunk_size, new_subchunk2_size, new_num_channels, header[7], bits)
    f_out.write(cod_data)
    f_out.close()

def decEstereo(ficCod, ficEste):
    f_in = open(ficCod, 'rb')
    header = read_wav_header(f_in)
    if header[6] != 1 or header[10] != 32:
        f_in.close()
        raise ValueError("The encoded file must be 32-bit mono")
    subchunk2_size = header[12]
    n_samples = subchunk2_size // (header[10] // 8)
    data = f_in.read(subchunk2_size)
    f_in.close()
    
    codes = struct.unpack('<' + 'i' * n_samples, data)
    
    left = []
    right = []
    for code in codes:
        s = code >> 16
        d = code & 0xFFFF
        if d >= 0x8000:
            d = d - 0x10000
        left.append(s + d)
        right.append(s - d)
    
    stereo_samples = []
    for i in range(n_samples):
        stereo_samples.append(left[i])
        stereo_samples.append(right[i])
    
    new_num_channels = 2
    bits = 16
    new_block_align = new_num_channels * (bits // 8)
    new_subchunk2_size = n_samples * new_block_align
    new_chunk_size = 36 + new_subchunk2_size
    stereo_data = struct.pack('<' + 'h' * (n_samples * 2), *stereo_samples)
    
    f_out = open(ficEste, 'wb')
    write_wav_header(f_out, new_chunk_size, new_subchunk2_size, new_num_channels, header[7], bits)
    f_out.write(stereo_data)
    f_out.close()