import tkinter as tk
from tkinter import filedialog, messagebox
from normaliza import normalizaHoras

class NormalizaApp:
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
    app = NormalizaApp(root)
    root.mainloop()
