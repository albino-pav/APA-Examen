Algorismia i Programació Audiovisual
====================================

Examen Final - Primavera de 2025
--------------------------------

<span style="color:red">Importante</span>
-----------------------------------------

Rellene la tabla siguiente con los nombres completos y la nota aspirada de cada participante. Recuerde que
si este examen se realiza en solitario, la nota aspirada es 10; si se realiza entre dos, la suma de las
notas aspiradas tiene que ser igual a 16; y si se realiza entre tres, las suma tiene que ser 18.

| Nombre completo              | Nota Aspirada |
| ---------------------------- | ------------- |
| Núria Rodríguez              | 10            |
| Ferran Gotarra               | 6             |


<span style="color:red">También Importante</span>
-------------------------------------------------

Se recuerda que los ejercicios más parecidos de lo razonable se repartirán la nota. Es decir, si dos ejercicios
merecedores de 10 se parecen mucho, la nota de cada uno será $10/2 = 5$; si
el parecido es entre tres ejercicios, la nota será $10/3=3,33$.

Ejercicio 1: Programa de Normalización de Expresiones Horarias (20%)
----------------------------------------------------------------------

- Construya el programa `normaliza.py`que permita leer un fichero de texto, normalice
  las expresiones horarias en él contenidas según las instrucciones de la tarea APA-T6
  y escriba el resultado en otro fichero de texto.
- El fichero de entrada y el nombre del fichero de salida tendrán la extensión `.txt` y
  se escogerán usando las funciones gráficas de `TkInter.filedialog`.
- No se evaluará la calidad de la normalización (ese aspecto se evalúa en APA-T6).

> **Respuesta:** `normaliza.py`

Ejercicio 2: Programa de Manejo de Señales Estéreo (35%)
--------------------------------------------------------

- Construya el programa `mono.py` que permita realizar las funciones de la tarea
  APA-T5 en un entorno gráfico usando TkInter.
- El programa contará con cuatro pestañas de `ttk.notebook`:

  - Pestaña `Estéreo a Mono`
  - Pestaña `Mono a Estéreo`
  - Pestaña `Codifica Estéreo`
  - Pestaña `Descodifica Estéreo`

  En cada una de estas pestañas se dispondrán de todos los artilugios necesarios para:
  
  - Seleccionar el o los ficheros de entrada.
  - Realizar la operación correspondiente.
  - Escuchar cada una de las señales involucradas, tanto de entrada como de salida.
  - Escribir la señal resultante en un fichero cuyo nombre se indicará al seleccionar la opción de `Guardar`.

- No se evaluará la corrección de las funciones desarrolladas en la tarea APA-T5, pero el programa deberá
  ser compatible con sus interfaces, de manera que, al susituir el
  `estereo.py` presentado por uno que funcione correctamente, el programa `mono.py` también lo hará.

> **Respuesta:** `mono.py`

Ejercicio 3: Programa de Visualización de Cuerpos Sometidos a Atracción Gravitatoria (45%)
---------------------------------------------------------------------------------------------

Realizar un programa de simulación de cuerpos celestes sometidos a la Ley de Gravitación Universal
de Newton. Como mínimo debe tener las mismas funcionalidades del programa `gravedad.exe` subido a Atenea
y hacerlo igual o mejor que éste.

> **Respuesta:** `graved.py`en bonito y `gravedad_.py` en básico. 
> Ambos códidos tienen exactamente las mismas funcionalidades, pero a causa de que la libreria `ttkbootstrap` no funciona siempre correctamente o da algunos problemillas, se ha optado por crear dos versiones del programa.

**Explicación de la aplicación:** 

En la parte de arriba, tiene un menú de opciones: 
- `Archivo` cuenta con `Guardar` y `Restaurar`. Cómo indican sus nombres, guardan y restauran el estado actual del programa utilizando el formato `json`.
- `Cuerpos` tiene las funcionalidades `Añadir cuerpo`, `Añadir cuerpo aleatorio` y `Editar cuerpo`.
- `Evaluación` cuenta con una nota estimada a partir del enunciado proporcionado.
- `Ayuda` tiene algunos consejos o información sobre el programa. 

A la izquierda, tenemos la pantalla de la simulación en cuestión.

Finalmente, a la derecha tenemos algunos atajos a funcionalidades mencionados anteriormente cómo `añadir cuerpo` y `añadir cuerpo aleatorio`. Además, cuenta con unas barras interactivas dónde te permite cambiar los valores de la constante de gravitación, los fps y el incremento del tiempo. También cuenta con un botón que permite cambiar el fondo de la simulación. 

A la hora de crear un cuerpo, el usuario tiene varios parámetros a completar: forma, tamaño, masa, opción de añadir cola, color, posiciónes x e y, al igual que las velocidades x e y, y el número de cuerpos que desea añadir con estas características. Los parámetros de posición y velodicad tienen la posibilidad de ser "randomizados". 

El fichero `ejemplo.json` contiene un escenario de ejemplo que puedes utilizar para probar el programa. Cómo he comentado antes, se carga des de `Archivo` > `Restaurar` > `ejemplo.json`.


Entrega
-------

Los tres programas deberán estar preparados para ser ejecutados desde la línea de comandos o desde
una sesión `ipython` usando el comando `%run`.
