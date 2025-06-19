import tkinter as tk
from tkinter import filedialog, messagebox
from horas import normalizaHoras

def main():
    root = tk.Tk()
    root.withdraw()

    # Selección del archivo de entrada
    entrada = filedialog.askopenfilename(
        title="Selecciona el archivo de entrada",
        filetypes=[("Fichero de texto", "*.txt")]
    )
    if not entrada:
        messagebox.showwarning("Aviso", "No se seleccionó archivo de entrada.")
        return

    # Selección del archivo de salida
    salida = filedialog.asksaveasfilename(
        title="Selecciona el archivo de salida",
        defaultextension=".txt",
        filetypes=[("Fichero de texto", "*.txt")]
    )
    if not salida:
        messagebox.showwarning("Aviso", "No se seleccionó archivo de salida.")
        return

    try:
        normalizaHoras(entrada, salida)
        messagebox.showinfo("Éxito", "Normalización completada correctamente.")
    except Exception as e:
        messagebox.showerror("Error", f"Se produjo un error:\n{e}")

    finally:
        root.destroy()

if __name__ == "__main__":
    main()