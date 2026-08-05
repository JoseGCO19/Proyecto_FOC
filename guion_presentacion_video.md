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
* **Lo que debes decir (Guión exacto):**
  > "¡Hola a todos! En este video explicaremos nuestra implementación del **Método Simplex Dual** en Python. El programa permite resolver problemas de optimización leyendo los datos directamente desde archivos `.txt` y mostrando el proceso iterativo paso a paso en consola."

---

### 1.2 Lógica Matemática del Simplex Dual (0:45 - 3:00)
* **Qué mostrar en pantalla:** Diapositiva con las fórmulas de selección de fila y columna pivote.

* **Lo que debes decir (Guión exacto y natural):**

  > **[1. Concepto y condición inicial]**  
  > "Para entender el Simplex Dual, primero debemos recordar la diferencia con el Simplex Primal tradicional.  
  > En el Simplex Primal empezamos con una solución *factible* (cumple las restricciones) e iteramos buscando la *optimalidad*.  
  > En cambio, en el **Simplex Dual** ocurre exactamente lo contrario: **empezamos con una solución óptima o Dual-Factible** (es decir, la fila $Z$ ya cumple con tener coeficientes $c_j \ge 0$), pero es **Primal-Infactible** (significa que tenemos valores negativos $b_i < 0$ en la columna de recursos RHS).  
  > El objetivo del Simplex Dual es eliminar gradualmente esas infactividades negativas hasta que todos los $b_i$ sean mayores o iguales a cero."

  > **[2. Criterio de la Variable que SALE - Fila Pivote]**  
  > "A diferencia del Simplex Primal donde primero se elige la columna, **en el Simplex Dual lo primero que elegimos es la Fila Pivote (la variable que sale de la base)**.  
  > La regla es muy sencilla: buscamos la fila con el **valor más negativo** en el lado derecho ($RHS$).  
  > Matemáticamente se expresa como:
  > $$r = \arg\min_i \{ b_i \mid b_i < 0 \}$$  
  > La fila elegida representa la restricción que tiene la peor infactibilidad, y su variable básica actual será la que **SALE** de la base."

  > **[3. Criterio de la Variable que ENTRA - Columna Pivote]**  
  > "Una vez seleccionada la fila que sale, necesitamos determinar qué variable **ENTRA** a la base (la Columna Pivote).  
  > Para esto seguimos dos pasos:  
  > 1. Miramos en la fila pivote únicamente aquellos coeficientes que sean **estrictamente negativos** ($a_{rj} < 0$).  
  > 2. Calculamos el cociente o razón en valor absoluto entre el coeficiente de la función objetivo ($c_j$) y el coeficiente negativo de la fila pivote ($a_{rj}$):  
  > $$\text{Cociente} = \left| \frac{c_j}{a_{rj}} \right|$$  
  > La variable que **ENTRA** a la base será aquella con el **cociente mínimo**:  
  > $$k = \arg\min_{a_{rj} < 0} \left| \frac{c_j}{a_{rj}} \right|$$  
  > *Nota:* Si ningún coeficiente en la fila pivote fuera negativo, significaría que el problema es totalmente infactible.  
  > Elegir el cociente mínimo es fundamental porque garantiza matemáticamente que, tras realizar el pivoteo por Gauss-Jordan, los coeficientes de la función objetivo se mantengan positivos ($c_j \ge 0$), conservando la dual-factibilidad en cada paso."

---

### 1.3 Lectura del Archivo `.txt` (3:00 - 4:15)
* **Qué mostrar en pantalla:** Abrir en el editor el código de la función `leer_problema_desde_txt()` y el archivo `problema.txt`.
* **Lo que debes decir (Guión exacto):**
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
