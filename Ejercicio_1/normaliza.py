import re
import tkinter as tk
from tkinter import filedialog
import os

'''
Oriol Jiménez Garrich
'''


'''
CONTENIDO APA-T6
'''

regex_hora_min = re.compile(r'\b(\d{1,2}):(\d{2})\b') # Format HH:MM o H:MM (dos dígits minuts obligatori)
regex_h_m = re.compile(r'\b(\d{1,2})h(?:(\d{1,2})m)?\b') # Format Hh o HhMm, p.e. 8h, 8h30m, 17h5m
regex_h_m_period = re.compile(r'\b(\d{1,2})h(?:(\d{1,2})m)?\s+de la (mañana|tarde|noche|madrugada|mediodía)\b')
regex_exp_12h = re.compile(r'\b(\d{1,2})\s+(y media|y cuarto|menos cuarto)\b') # Format "X y media", "X y cuarto", "X menos cuarto"
regex_exp_12h_period = re.compile(
	r'\b(\d{1,2})\s+(y media|y cuarto|menos cuarto)\s+de la\s+'
	r'(mañana|tarde|noche|madrugada|mediodía)\b'
)
regex_en_punto = re.compile(r'\b(\d{1,2})\s+en punto\b') # Format "X en punto"
regex_periodo = re.compile(r'\b(\d{1,2})\s+de la (mañana|tarde|noche|madrugada|mediodía)\b') # Format "X de la mañana", "X de la tarde", ...

def normalitza_exp_12h_period(match):
	h = int(match.group(1))
	parte = match.group(2)
	periodo = match.group(3)
	if parte == 'y media':
		m = 30
	elif parte == 'y cuarto':
		m = 15
	else:
		m = 45
		h = h-1 if h>1 else 12
	h24 = converteix_12h_a_24h(h, periodo)
	if not es_hora_valida(h24, m):
		return match.group(0)
	return f'{h24:02d}:{m:02d}'

def es_hora_valida(h, m):
	return 0 <= h <= 23 and 0 <= m <= 59

def converteix_12h_a_24h(h, periodo):
	if periodo == 'noche' and h == 12:
		return 0
	if h == 12:
		h = 0
	if periodo == 'mañana':
		return h
	elif periodo == 'mediodía':
		return h + 12 if h < 12 else h
	elif periodo == 'tarde' or periodo == 'noche' or periodo == 'madrugada':
		return h + 12
	else:
		return h
	
def normalitza_hora_min(match):
	h = int(match.group(1))
	m = int(match.group(2))
	if es_hora_valida(h, m):
		return f'{h:02d}:{m:02d}'
	else:
		return match.group(0)

def normalitza_h_m(match):
	h = int(match.group(1))
	m = int(match.group(2)) if match.group(2) else 0
	if es_hora_valida(h, m):
		return f'{h:02d}:{m:02d}'
	else:
		return match.group(0)
	
def normalitza_h_m_period(match):
	h = int(match.group(1))
	m = int(match.group(2)) if match.group(2) else 0
	periodo = match.group(3)
	valid = {
		'mañana':   lambda x: 1 <= x <= 11,
		'mediodía': lambda x: x == 12,
		'tarde':    lambda x: 3 <= x <= 8,
		'noche':    lambda x: (8 <= x <= 12) or (1 <= x <= 4),
		'madrugada':lambda x: 1 <= x <= 6,
	}
	if not valid[periodo](h) or not es_hora_valida(h, m):
		return match.group(0)
	h24 = converteix_12h_a_24h(h, periodo)
	return f'{h24:02d}:{m:02d}'
	
def normalitza_exp_12h(match):
	h = int(match.group(1))
	part = match.group(2)
	if not (1 <= h <= 12):
		return match.group(0)
	if part == 'y media':
		m = 30
	elif part == 'y cuarto':
		m = 15
	elif part == 'menos cuarto':
		m = 45
		h = h - 1 if h > 1 else 12
	else:
		return match.group(0)
	if not (1 <= h <= 12):
		return match.group(0)
	return f'{h:02d}:{m:02d}'

def normalitza_en_punto(match):
	h = int(match.group(1))
	if 0 <= h <= 23:
		return f'{h:02d}:00'
	return match.group(0)

def normalitza_periodo(match):
	h = int(match.group(1))
	periodo = match.group(2)
	valid = {
		'mañana':   lambda x: 1 <= x <= 11,
		'mediodía': lambda x: x == 12,
		'tarde':    lambda x: 3 <= x <= 8,
		'noche':    lambda x: (8 <= x <= 12) or (1 <= x <= 4),
		'madrugada':lambda x: 1 <= x <= 6,
	}
	if not valid[periodo](h):
		return match.group(0)
	h24 = converteix_12h_a_24h(h, periodo)
	if not es_hora_valida(h24, 0):
		return match.group(0)
	return f'{h24:02d}:00'

def normalizaHoras(ficText, ficNorm):
	with open(ficText, 'r', encoding='utf-8') as f_in, open(ficNorm, 'w', encoding='utf-8') as f_out:
		for linia in f_in:
			linia = regex_exp_12h_period.sub(normalitza_exp_12h_period, linia)
			linia = regex_h_m_period.sub(normalitza_h_m_period, linia)
			linia = regex_h_m.sub(normalitza_h_m, linia)
			linia = regex_hora_min.sub(normalitza_hora_min, linia)
			linia = regex_exp_12h.sub(normalitza_exp_12h, linia)
			linia = regex_en_punto.sub(normalitza_en_punto, linia)
			linia = regex_periodo.sub(normalitza_periodo, linia)
			f_out.write(linia)
			

'''
CONTENIDO NUEVO
'''

def crear_ventana():
	ventana = tk.Tk()
	ventana.withdraw()
	
	fichero = filedialog.askopenfile(title="Seleccione el fichero de entrada", filetypes=[("Text files", "*.txt")])
	if not fichero:
		print("No se ha seleccionado ningun fichero")
		return
	
	nombre = fichero.name
	nombre = os.path.splitext(nombre)[0]
	ficheroNormalizado = nombre + "_normalizado.txt"

	normalizaHoras(fichero.name, ficheroNormalizado)
	print(f"Fichero {ficheroNormalizado} creado y normalizado correctamente")
	fichero.close()


if __name__ == '__main__':
	crear_ventana()
