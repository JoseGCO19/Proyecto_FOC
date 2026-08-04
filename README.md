# Método Simplex Dual - Solucionador Computacional Paso a Paso

Implementación computacional del **Algoritmo del Método Simplex Dual** desarrollada en Python para la resolución de Problemas de Programación Lineal (PL). Este programa comprende los criterios de factibilidad dual, optimalidad primal, prueba del cociente dual y transiciones explícitas entre diccionarios de Dantzig y tablas Simplex.

---

## 🌟 Características Principales

1. **Aritmética Exacta con Fracciones**:
   - Utiliza `fractions.Fraction` de Python para realizar cálculos racionales exactos (`3/4`, `-10/3`), evitando imprecisiones de redondeo de punto flotante.
   - Opción para conmutar a modo decimal con precisión configurable.

2. **Doble Representación**:
   - **Diccionario de Dantzig**: $x_{B_i} = b_i + \sum d_{ij} x_{N_j}$
   - **Tabla Simplex Canónica**: Matriz con fila $Z$ y filas de restricciones.

3. **Explicación Detallada Paso a Paso**:
   - **Criterio de Salida ($x_{sale}$)**: Identificación de filas básicas infactibles ($b_i < 0$) y aplicación de la Regla de Bland o Selección de Mayor Infactibilidad.
   - **Prueba del Cociente Dual**: Detalle de $\theta_j = \left| \frac{c_j}{d_{sale, j}} \right|$ para coeficientes $d_{sale, j} > 0$.
   - **Criterio de Entrada ($x_{entra}$)**: Elección del menor cociente dual para mantener la factibilidad dual.
   - **Detección de Estados**: Solución Óptima, Infactibilidad Primal (Dual No Acotado) y Detección de Ciclaje.

4. **Interfaz de Consola (CLI) e Interfaz Web Interactiva (GUI)**:
   - CLI rápida en terminal con exportación a archivos Markdown/Texto.
   - Web App moderna con soporte MathJax/LaTeX, navegación interactiva entre pasos y resaltado de la celda pivote.

5. **Lector Universal de Archivos**:
   - Entrada en texto algebraico libre (e.g. `MAX z = -3x1 - 2x2`, `s.t.`, `>=`, `<=`).
   - Entrada en formato matricial JSON ($A, b, c$).

---

## 🚀 Guía de Uso

### 1. Ejecución en Consola (CLI)

Para resolver un problema desde un archivo de texto o JSON:

```bash
python main.py -f examples/problema_estandar.txt
```

Para guardar el informe paso a paso en un archivo Markdown:

```bash
python main.py -f examples/problema_estandar.txt -o reporte.md
```

Para ingresar un problema de forma interactiva desde la terminal:

```bash
python main.py
```

### 2. Ejecución de la Interfaz Web Interactiva

Para iniciar el servidor web interactivo:

```bash
python main.py --web
```
o ejecutando directamente:
```bash
python web/app.py
```

Abra su navegador en: `http://127.0.0.1:8000/`

---

## 📁 Formatos de Entrada Admitidos

### Formato Texto Algebraico (`.txt`)
```text
MAX z = -3 x1 - 2 x2
s.t.
x1 + 2 x2 >= 6
2 x1 + x2 >= 8
x1, x2 >= 0
```

### Formato Matricial JSON (`.json`)
```json
{
  "sense": "MAX",
  "c": [-3, -4, -1],
  "A": [
    [-1, -2, -1],
    [-2, -1, -3]
  ],
  "b": [-6, -8],
  "ops": ["<=", "<="],
  "var_names": ["x1", "x2", "x3"]
}
```

---

## 🧪 Pruebas Unitarias

Ejecute la suite de pruebas automatizadas:

```bash
python test_dual_simplex.py
```

---

## 📖 Estructura del Código

- `core/dual_simplex.py`: Motor principal del algoritmo Simplex Dual y estructuras `Dictionary` y `StepRecord`.
- `core/lp_parser.py`: Analizador de funciones objetivo y restricciones algebraicas / matriciales.
- `core/fraction_utils.py`: Herramientas de formateo numérico exacto y conversión LaTeX.
- `web/app.py`: Servidor HTTP/API REST.
- `web/templates/index.html` & `web/static/`: Interfaz gráfica interactiva.
- `main.py`: Punto de entrada CLI y ejecutable de la aplicación.
