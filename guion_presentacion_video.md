# 🎬 Guión para Video de Presentación: Simplex Dual en Python
**Duración Máxima:** 10 minutos (Estimado: 8:30 a 9:00 minutos)  
**Modalidad:** Pareja (Estudiante 1 y Estudiante 2)

---

## ⏱️ Distribución del Tiempo

| Parte | Encargado | Tema Principal | Tiempo Estimado |
| :--- | :--- | :--- | :--- |
| **Parte 1** | **Estudiante 1** | Introducción, Teoría Matemática y Lectura de Archivo `.txt` | **0:00 a 4:15 min** (4:15 min) |
| **Parte 2** | **Estudiante 2** | Código del Algoritmo, Ejemplo en Vivo en Terminal y Cierre | **4:15 a 9:00 min** (4:45 min) |

---

## 👥 PARTE 1: Teoría Matemática y Carga de Archivo (Estudiante 1)
**Tiempo:** 0:00 a 4:15 min (Duración: 4:15 min)

### 1.1 Introducción (0:00 - 0:45)
* **Qué mostrar en pantalla:** Diapositiva inicial con el título del proyecto y los nombres de los dos integrantes.
* **Lo que debes decir:**
  > "¡Hola a todos! En este video explicaremos nuestra implementación del **Método Simplex Dual** en Python. El programa permite resolver problemas de optimización leyendo los datos directamente desde archivos `.txt` y mostrando el proceso iterativo en consola."

### 1.2 Lógica Matemática del Simplex Dual (0:45 - 3:00)
* **Qué mostrar en pantalla:** Diapositiva con las 2 fórmulas principales.
* **Puntos a explicar:**
  1. **¿Cuándo se usa?**: Se aplica cuando la solución es **Dual-Factible** (coeficientes objetivo $c_j \ge 0$), pero **Primal-Infactible** (hay valores $b_i < 0$ en el lado derecho RHS).
  2. **Variable que Sale (Fila Pivote):** Elegimos la fila con el valor $b_i$ más negativo en el lado derecho:
     $$r = \arg\min \{ b_i \mid b_i < 0 \}$$
  3. **Variable que Entra (Columna Pivote):** Entre las columnas que tengan coeficientes negativos en la fila pivote ($a_{rj} < 0$), elegimos la que tenga el menor cociente en valor absoluto:
     $$k = \arg\min_{a_{rj} < 0} \left| \frac{c_j}{a_{rj}} \right|$$

### 1.3 Lectura del Archivo `.txt` (3:00 - 4:15)
* **Qué mostrar en pantalla:** Abrir en el editor el código de la función `leer_problema_desde_txt()` y el archivo `problema.txt`.
* **Lo que debes decir:**
  > "Nuestra función `leer_problema_desde_txt()` en `simplex_dual.py` es muy flexible:
  > - Ignora automáticamente líneas de comentarios que inicien con `#`.
  > - Soporta 3 formatos de entrada: clave-valor (`tipo: min`, `c: 3, 2`), notación algebraica (`min z = 3x1 + 2x2`) o formato JSON.
  > - Convierte los datos en un diccionario que luego genera el Tableau inicial en Pandas con sus variables de holgura (`h1`, `h2`)."

---

## 👥 PARTE 2: Recorrido del Código, Demostración y Cierre (Estudiante 2)
**Tiempo:** 4:15 a 9:00 min (Duración: 4:45 min)

### 2.1 Explicación del Algoritmo Principal (4:15 - 6:45)
* **Qué mostrar en pantalla:** La función `metodo_simplex_dual()` en `simplex_dual.py`.
* **Puntos clave a mostrar en el código:**
  1. **Condición de Parada:** El bucle termina cuando todos los valores del RHS son mayores o iguales a cero (`np.all(b >= -1e-10)`).
  2. **Selección Fila y Columna:** Usamos `b.argmin()` para obtener la fila saliente e `idxmin()` sobre los cocientes para la columna entrante.
  3. **Pivoteo Gauss-Jordan:** Normalizamos la fila pivote dividiendo por el elemento pivote e iteramos haciendo ceros en el resto de la columna.
  4. **Actualización de la Tabla:** Modificamos el índice de Pandas `df.index` para cambiar el nombre de la variable básica.

### 2.2 Demostración corriendo en Vivo en Terminal (6:45 - 8:30)
* **Qué mostrar en pantalla:** Terminal (PowerShell o CMD) en la carpeta del proyecto.
* **Comando a ejecutar:**
  ```bash
  python simplex_dual.py problema.txt
  ```
* **Qué ir comentando durante la ejecución:**
  1. Mostrar que la terminal lee `problema.txt` e imprime el diccionario procesado.
  2. Mostrar el Tableau Inicial generado con las holguras `h1 = -6` y `h2 = -4`.
  3. Comentar la Iteración 1 (sale `h1`, entra `x1`) y la Iteración 2 (sale `h2`, entra `x2`).
  4. Mostrar el Tableau Final Óptimo alcanzado y la solución final: $x_1 = 2.0$, $x_2 = 2.0$ y el valor óptimo de $Z = 10.00$.

### 2.3 Conclusiones y Despedida (8:30 - 9:00)
* **Qué mostrar en pantalla:** Diapositiva final de cierre.
* **Lo que debes decir:**
  > "Como pudimos observar, el programa resuelve el problema en 2 iteraciones, ofreciendo la comodidad de leer archivos `.txt` en distintos formatos y utilizando Pandas y NumPy para mantener el código claro y corto. ¡Muchas gracias por su atención!"
