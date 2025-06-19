import tkinter as tk
from tkinter import filedialog, messagebox
import re

def normalizaHoras(ficText, ficNorm):
    def rojo(texto):
        return f'<span style = "color:red">{texto}</span>'

    def reemplaza(match):
        grupo = match.group()

        h_m = re.match(r'^(\d{1,2})h(?:(\d{1,2})m?)?$', grupo)
        if h_m:
            h = int(h_m.group(1))
            m_str = h_m.group(2)
            m = int(m_str) if m_str else 0
            return f'{h}:{m:02d}' if h < 24 and m < 60 else rojo(grupo)

        h_p_m = re.match(r'^(\d{1,2}):(\d{1,2})$', grupo)
        if h_p_m:
            h = int(h_p_m.group(1))
            m_str = h_p_m.group(2)
            m = int(m_str)
            return f'{h}:{m:02d}' if h < 24 and m < 60 and len(m_str) == 2 else rojo(grupo)

        hablado = re.match(r'^(\d{1,2})\s*(en punto|y cuarto|y media|menos cuarto)$', grupo)
        if hablado:
            h = int(hablado.group(1))
            f = hablado.group(2)
            if not (1 <= h <= 12):
                return rojo(grupo)
            m = {'en punto': 0, 'y cuarto': 15, 'y media': 30, 'menos cuarto': 45}[f]
            if f == 'menos cuarto':
                h = 12 if h == 1 else h - 1
            return f'{h}:{m:02d}'

        hablado_momento = re.match(r'^(\d{1,2})\s*(en punto|y cuarto|y media|menos cuarto)\s+de la\s+(mañana|tarde|noche)$', grupo)
        if hablado_momento:
            h = int(hablado_momento.group(1))
            f = hablado_momento.group(2)
            p = hablado_momento.group(3)
            m = {'en punto': 0, 'y cuarto': 15, 'y media': 30, 'menos cuarto': 45}[f]
            if f == 'menos cuarto':
                h = 12 if h == 1 else h - 1
            if p == 'tarde' and 1 <= h <= 7:
                h += 12
            elif p == 'noche':
                if 8 <= h <= 11:
                    h += 12
                elif h == 12:
                    return '00:00'
            return f'{h}:{m:02d}'

        momento = re.match(r'^(\d{1,2})\s+de la\s+(mañana|tarde|noche)$', grupo)
        if momento:
            h = int(momento.group(1))
            p = momento.group(2)
            if p == 'mañana':
                if 1 <= h <= 11:
                    return f'{h}:00'
                else:
                    return rojo(grupo)
            elif p == 'tarde':
                if 1 <= h <= 7:
                    return f'{h+12}:00'
                else:
                    return rojo(grupo)
            elif p == 'noche':
                if 8 <= h <= 11:
                    return f'{h+12}:00'
                elif h == 12:
                    return '00:00'
                else:
                    return rojo(grupo)

        return rojo(grupo)

    compila = re.compile(
        r'\b\d{1,2}h(?:\d{1,2}m?)?'
        r'|\b\d{1,2}:\d{1,2}'
        r'|\b\d{1,2}\s*(?:en punto|y cuarto|y media|menos cuarto)(?:\s+de la\s+(?:mañana|tarde|noche))?'
        r'|\b\d{1,2}\s+de la\s+(?:mañana|tarde|noche)'
        r'|(?<=\blas\s)\d{1,2}\b'
        r'|(?<=\ba las\s)\d{1,2}\b'
    )

    with open(ficText, encoding='utf-8') as entrada, open(ficNorm, 'w', encoding='utf-8') as salida:
        salida.write('<htm><body><pre style="font-family:monospace;">\n')
        for linea in entrada:
            nueva = compila.sub(reemplaza, linea)
            nueva = re.sub(r'\s+de la (mañana|tarde|noche)', '', nueva, flags=re.IGNORECASE)
            salida.write(nueva)
        salida.write('</pre></body></html>')

class MenuInteractivo:
    def __init__(self, root):
        self.root = root
        root.title("Normalizador de Horas")

        tk.Label(root, text="Normalizar expresiones de hora en un fichero de texto").pack(pady=10)
        
        tk.Button(root, text="Seleccionar fichero de entrada", command=self.seleccionar_entrada).pack(pady=5)
        tk.Button(root, text="Guardar fichero normalizado como...", command=self.seleccionar_salida).pack(pady=5)

        self.lbl_entrada = tk.Label(root, text="Archivo de entrada: (no seleccionado)")
        self.lbl_entrada.pack(pady=2)

        self.lbl_salida = tk.Label(root, text="Archivo de salida: (no seleccionado)")
        self.lbl_salida.pack(pady=2)

        tk.Button(root, text="Ejecutar normalización", command=self.normalizar).pack(pady=10)

        self.ficText = None
        self.ficNorm = None

    def seleccionar_entrada(self):
        self.ficText = filedialog.askopenfilename(title="Selecciona el fichero de entrada", filetypes=[("Text files", "*.txt")])
        if self.ficText:
            self.lbl_entrada.config(text=f"Archivo de entrada: {self.ficText}")

    def seleccionar_salida(self):
        self.ficNorm = filedialog.asksaveasfilename(title="Selecciona el nombre del fichero de salida", defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if self.ficNorm:
            self.lbl_salida.config(text=f"Archivo de salida: {self.ficNorm}")

    def normalizar(self):
        if not self.ficText or not self.ficNorm:
            messagebox.showerror("Error", "Debes seleccionar ambos ficheros")
            return
        try:
            normalizaHoras(self.ficText, self.ficNorm)
            messagebox.showinfo("Éxito", "Archivo normalizado correctamente")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == '__main__':
    root = tk.Tk()
    app = MenuInteractivo(root)
    root.mainloop()
