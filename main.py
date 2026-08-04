import sys
import argparse
from typing import List
from core.lp_parser import LPParser
from core.dual_simplex import DualSimplexSolver, StepRecord, Dictionary
from core.fraction_utils import format_fraction, parse_number

def render_step_ascii(step: StepRecord, mode: str = "fraction") -> str:
    lines = []
    lines.append("=" * 70)
    lines.append(f"  ITERACIÓN {step.iteration}")
    lines.append("=" * 70)
    
    # 1. Representación de Diccionario
    d_data = step.dictionary.to_dict_repr(mode=mode)
    lines.append("\n--- Diccionario de Dantzig ---")
    lines.append(d_data["z_equation"])
    for eq in d_data["equations"]:
        lines.append("  " + eq)

    # 2. Representación de Tabla Simplex
    tab = step.dictionary.to_tableau_repr(mode=mode)
    lines.append("\n--- Tabla Simplex Canónica ---")
    
    # Formateador de tabla
    headers = ["Base"] + tab["headers"]
    col_widths = [max(len(h), 8) for h in headers]
    
    header_str = " | ".join(f"{h:^{col_widths[idx]}}" for idx, h in enumerate(headers))
    sep_str = "-+-".join("-" * col_widths[idx] for idx in range(len(headers)))
    
    lines.append(header_str)
    lines.append(sep_str)
    
    # Fila Z
    z_cells = ["Z"] + tab["z_row"]
    lines.append(" | ".join(f"{z_cells[idx]:^{col_widths[idx]}}" for idx in range(len(z_cells))))
    lines.append(sep_str)
    
    # Filas de Restricciones
    for row in tab["rows"]:
        cells = [row["var"]] + row["row"]
        lines.append(" | ".join(f"{cells[idx]:^{col_widths[idx]}}" for idx in range(len(cells))))
    lines.append(sep_str)

    # 3. Transición y Criterios
    lines.append("\n--- Criterios de Transición ---")
    if step.status == "OPTIMAL":
        lines.append(">>> ESTADO: SOLUCIÓN ÓPTIMA ALCANZADA <<<")
        lines.append("Factibilidad Primal: SÍ (Todos los b_i >= 0)")
        lines.append("Factibilidad Dual: SÍ (Coeficientes en Z <= 0)")
        lines.append("\nSolución Óptima:")
        sol = step.dictionary.get_primal_solution()
        for k, v in sol.items():
            lines.append(f"  {k} = {format_fraction(v, mode=mode)}")
        lines.append(f"Valor Óptimo Z = {format_fraction(step.dictionary.get_objective_value(), mode=mode)}")
    
    elif step.status == "INFEASIBLE":
        lines.append(">>> ESTADO: PROBLEMA INFACTIBLE (DUAL NO ACOTADO) <<<")
        lines.append(f"Variable de Salida seleccionada: {step.leaving_var}")
        lines.append("Prueba del Cociente Dual: No existe ninguna variable no básica con coef d_ij > 0 en esta fila.")
        lines.append(step.explanation)
        
    elif step.status == "NOT_DUAL_FEASIBLE":
        lines.append(">>> ESTADO: ERROR - DICCIONARIO NO ES DUAL FACTIBLE <<<")
        lines.append(step.explanation)

    else:
        lines.append(f"1. Variable que sale (x_sale): {step.leaving_var}  (b_{step.leaving_var} = {step.dictionary.b[step.leaving_index]})")
        lines.append("2. Prueba del cociente dual theta_j = |c_j / d_{sale, j}| para d_{sale, j} > 0:")
        for nb_var, ratio in step.ratio_tests.items():
            if ratio is not None:
                lines.append(f"   - {nb_var}: ratio = {ratio}")
            else:
                lines.append(f"   - {nb_var}: no elegible (d <= 0)")
        lines.append(f"3. Variable que entra (x_entra): {step.entering_var} (cociente mínimo)")
        lines.append(f"4. Elemento Pivote: {step.pivot_element}")

    lines.append("\n")
    return "\n".join(lines)


def prompt_guided_input() -> Dictionary:
    print("==========================================================")
    print("      INGRESO INTERACTIVO DE PROGRAMACIÓN LINEAL         ")
    print("==========================================================")
    print("Seleccione la modalidad de ingreso:")
    print("  1. Guiado por número de variables y restricciones (Recomendado)")
    print("  2. Texto algebraico libre (e.g. MAX z = -3x1 - 2x2...)")
    
    choice = input("\nOpción (1 u 2) [1]: ").strip()
    if choice == "2":
        print("\nIngrese el problema en texto algebraico (presione Enter en línea vacía al finalizar):")
        print("Ejemplo:\n  MAX z = -3 x1 - 2 x2\n  s.t.\n  x1 + 2 x2 >= 6\n  2 x1 + x2 >= 8")
        print("---------------------------------------")
        lines = []
        try:
            while True:
                line = input()
                if not line.strip() and len(lines) >= 2:
                    break
                lines.append(line)
        except EOFError:
            pass
        return LPParser.parse_text_algebraic("\n".join(lines))

    # Modo 1: Guiado por variables y restricciones
    print("\n--- MODO GUIADO ---")
    
    # 1. Número de variables
    while True:
        try:
            n_vars_str = input("1. ¿Cuántas VARIABLES de decisión se usarán? (e.g. 2): ").strip()
            n_vars = int(n_vars_str)
            if n_vars > 0:
                break
            print("   El número de variables debe ser mayor a 0.")
        except ValueError:
            print("   Por favor ingrese un entero válido (ejemplo: 2).")

    var_names = [f"x{i+1}" for i in range(n_vars)]
    print(f"   -> Variables que se utilizarán: {', '.join(var_names)}")

    # 2. Número de restricciones
    while True:
        try:
            m_const_str = input("\n2. ¿Cuántas RESTRICCIONES se usarán? (e.g. 6 o más): ").strip()
            m_const = int(m_const_str)
            if m_const > 0:
                break
            print("   El número de restricciones debe ser mayor a 0.")
        except ValueError:
            print("   Por favor ingrese un entero válido (ejemplo: 6).")

    # 3. Sentido de optimización
    print("\n3. ¿Sentido de Optimización?")
    print("   1: Maximizar (MAX)")
    print("   2: Minimizar (MIN)")
    sense_opt = input("   Selección (1 u 2) [1]: ").strip()
    sense = "MIN" if sense_opt == "2" else "MAX"

    # 4. Coeficientes de la Función Objetivo
    print(f"\n4. Función Objetivo ({sense} z):")
    print(f"   Ingrese los {n_vars} coeficientes para ({', '.join(var_names)}).")
    print("   (Puede ingresarlos separados por espacio o uno por uno)")
    
    c_coeffs = []
    raw_c = input("   Coeficientes de Z: ").strip()
    if raw_c:
        tokens = [t for t in raw_c.replace(",", " ").split() if t]
        for tok in tokens[:n_vars]:
            try:
                c_coeffs.append(parse_number(tok))
            except ValueError:
                pass
                
    while len(c_coeffs) < n_vars:
        curr_var = var_names[len(c_coeffs)]
        try:
            val_str = input(f"   - Coeficiente de {curr_var}: ").strip()
            c_coeffs.append(parse_number(val_str))
        except ValueError:
            print("     Valor inválido. Ejemplo: -3, 2/5, 0.5")

    # 5. Restricciones
    print(f"\n5. Ingrese las {m_const} restricciones:")
    A_matrix = []
    b_vector = []
    ops_list = []

    for i in range(m_const):
        print(f"\n--- Restricción {i+1} de {m_const} ---")
        row = []
        print(f"   Ingrese los {n_vars} coeficientes para ({', '.join(var_names)}):")
        raw_row = input(f"   Row {i+1} Coeficientes: ").strip()
        if raw_row:
            tokens = [t for t in raw_row.replace(",", " ").split() if t]
            for tok in tokens[:n_vars]:
                try:
                    row.append(parse_number(tok))
                except ValueError:
                    pass
        
        while len(row) < n_vars:
            curr_var = var_names[len(row)]
            try:
                val_str = input(f"   - Coeficiente de {curr_var}: ").strip()
                row.append(parse_number(val_str))
            except ValueError:
                print("     Valor inválido. Ejemplo: 1, -2, 3/4")

        while True:
            op = input("   Operación de Restricción (<=, >=, =): ").strip()
            if op in ["<=", ">=", "="]:
                break
            print("   Operador inválido. Use '<=', '>=' o '='.")
        
        while True:
            try:
                b_str = input("   Valor del Lado Derecho (b): ").strip()
                b_val = parse_number(b_str)
                break
            except ValueError:
                print("   Valor inválido. Ingrese un número o fracción.")

        A_matrix.append(row)
        b_vector.append(b_val)
        ops_list.append(op)

    json_data = {
        "sense": sense,
        "c": c_coeffs,
        "A": A_matrix,
        "b": b_vector,
        "ops": ops_list,
        "var_names": var_names
    }

    return LPParser.from_json_dict(json_data)


def run_cli(file_path: str = None, mode: str = "fraction", output_file: str = None):
    if file_path:
        print(f"Cargando problema desde: {file_path}")
        dictionary = LPParser.from_file(file_path)
    else:
        dictionary = prompt_guided_input()

    solver = DualSimplexSolver(dictionary)
    history = solver.solve()

    full_output = []
    for step in history:
        rendered = render_step_ascii(step, mode=mode)
        print(rendered)
        full_output.append(rendered)

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(full_output))
        print(f"Reporte guardado exitosamente en: {output_file}")


def start_web_server(host: str = "127.0.0.1", port: int = 8000):
    try:
        import uvicorn
        from web.app import app
        print(f"Iniciando Servidor Web en http://{host}:{port}")
        uvicorn.run(app, host=host, port=port)
    except ImportError:
        print("Error: Para ejecutar la interfaz web se requieren 'uvicorn' y 'fastapi'.")
        print("Instálelos usando: pip install fastapi uvicorn")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Método Simplex Dual en Python")
    parser.add_argument("--file", "-f", help="Ruta al archivo del problema (.txt o .json)", default=None)
    parser.add_argument("--mode", "-m", choices=["fraction", "decimal"], default="fraction", help="Modo de aritmética (fracción exacta o decimal)")
    parser.add_argument("--output", "-o", help="Archivo donde guardar el informe paso a paso", default=None)
    parser.add_argument("--web", "-w", action="store_true", help="Iniciar la interfaz gráfica web interactiva")
    parser.add_argument("--port", "-p", type=int, default=8000, help="Puerto para el servidor web")

    args = parser.parse_args()

    if args.web:
        start_web_server(port=args.port)
    else:
        run_cli(file_path=args.file, mode=args.mode, output_file=args.output)
