from fractions import Fraction
from typing import List, Dict, Tuple, Optional, Any, Union
from core.fraction_utils import parse_number, format_fraction

class Dictionary:
    """
    Representa un Diccionario Simplex de Dantzig:
    x_B[i] = b[i] + sum_{j in N} d[i][j] * x_N[j]
    z = z0 + sum_{j in N} c[j] * x_N[j]
    
    Donde:
    - basic_vars: Lista de nombres de variables básicas [x_B1, x_B2, ...]
    - non_basic_vars: Lista de nombres de variables no básicas [x_N1, x_N2, ...]
    - b: Vector constante para variables básicas (longitud m)
    - d: Matriz de coeficientes de las variables no básicas en las ecuaciones básicas (m x n)
         Nota: x_Bi = b_i + sum_j d_{ij} x_Nj  (es decir, d_{ij} = -a_{ij} de la tabla standard)
    - c: Coeficientes de la función objetivo para variables no básicas (longitud n)
    - z0: Valor constante de la función objetivo
    - sense: 'MAX' o 'MIN'
    """
    def __init__(
        self,
        basic_vars: List[str],
        non_basic_vars: List[str],
        b: List[Union[Fraction, int, str]],
        d: List[List[Union[Fraction, int, str]]],
        c: List[Union[Fraction, int, str]],
        z0: Union[Fraction, int, str] = 0,
        sense: str = "MAX"
    ):
        self.basic_vars = list(basic_vars)
        self.non_basic_vars = list(non_basic_vars)
        self.b = [parse_number(x) for x in b]
        self.d = [[parse_number(val) for val in row] for row in d]
        self.c = [parse_number(x) for x in c]
        self.z0 = parse_number(z0)
        self.sense = sense.upper()

    def copy(self) -> 'Dictionary':
        return Dictionary(
            basic_vars=list(self.basic_vars),
            non_basic_vars=list(self.non_basic_vars),
            b=list(self.b),
            d=[list(row) for row in self.d],
            c=list(self.c),
            z0=self.z0,
            sense=self.sense
        )

    def is_dual_feasible(self) -> bool:
        """
        En Maximización, el diccionario es dual-factible si todos los coeficientes
        de las variables no básicas en la función objetivo son <= 0 (c_j <= 0).
        En Minimización (si z se minimiza), equivale a c_j >= 0.
        """
        if self.sense == "MAX":
            return all(cj <= 0 for cj in self.c)
        else:
            return all(cj >= 0 for cj in self.c)

    def is_primal_feasible(self) -> bool:
        """
        Es primal-factible si todas las constantes b_i son >= 0.
        """
        return all(bi >= 0 for bi in self.b)

    def get_primal_solution(self) -> Dict[str, Fraction]:
        """
        Devuelve el valor actual de todas las variables en la solución básica.
        """
        sol = {}
        for var in self.non_basic_vars:
            sol[var] = Fraction(0)
        for i, var in enumerate(self.basic_vars):
            sol[var] = self.b[i]
        return sol

    def get_objective_value(self) -> Fraction:
        return self.z0

    def to_dict_repr(self, mode: str = "fraction") -> Dict[str, Any]:
        """
        Exporta el diccionario en formato legible para la API / Web UI.
        """
        equations = []
        for i, b_var in enumerate(self.basic_vars):
            terms = [format_fraction(self.b[i], mode=mode)]
            for j, nb_var in enumerate(self.non_basic_vars):
                coeff = self.d[i][j]
                if coeff != 0:
                    coeff_str = format_fraction(coeff, mode=mode)
                    if coeff > 0 and terms:
                        terms.append(f"+ {coeff_str} {nb_var}")
                    elif coeff < 0:
                        if coeff == -1:
                            terms.append(f"- {nb_var}")
                        else:
                            terms.append(f"- {format_fraction(-coeff, mode=mode)} {nb_var}")
                    else:
                        if coeff == 1:
                            terms.append(f"+ {nb_var}")
                        else:
                            terms.append(f"+ {coeff_str} {nb_var}")
            equations.append(f"{b_var} = " + " ".join(terms))

        z_terms = [format_fraction(self.z0, mode=mode)]
        for j, nb_var in enumerate(self.non_basic_vars):
            coeff = self.c[j]
            if coeff != 0:
                coeff_str = format_fraction(coeff, mode=mode)
                if coeff > 0:
                    terms_sign = f"+ {coeff_str} {nb_var}" if coeff != 1 else f"+ {nb_var}"
                else:
                    terms_sign = f"- {format_fraction(-coeff, mode=mode)} {nb_var}" if coeff != -1 else f"- {nb_var}"
                z_terms.append(terms_sign)

        z_eq = f"z = " + " ".join(z_terms)

        return {
            "basic_vars": self.basic_vars,
            "non_basic_vars": self.non_basic_vars,
            "b": [format_fraction(x, mode=mode) for x in self.b],
            "d": [[format_fraction(val, mode=mode) for val in row] for row in self.d],
            "c": [format_fraction(x, mode=mode) for x in self.c],
            "z0": format_fraction(self.z0, mode=mode),
            "equations": equations,
            "z_equation": z_eq,
            "sense": self.sense
        }

    def to_tableau_repr(self, mode: str = "fraction") -> Dict[str, Any]:
        """
        Convierte la representación de diccionario a la Tabla Simplex canónica:
        Fila Z: z - sum(c_j * x_j) = z0
        Filas Restricción: x_Bi - sum(d_ij * x_j) = b_i   (o x_Bi + sum(a_ij * x_j) = b_i)
        """
        all_vars = self.non_basic_vars + self.basic_vars
        headers = list(all_vars) + ["RHS"]
        
        rows = []
        # Fila del objetivo Z: z - c_N x_N = z0
        z_row = []
        for v in all_vars:
            if v in self.non_basic_vars:
                j = self.non_basic_vars.index(v)
                # En la tabla standard, el coeficiente en fila Z es -c_j para MAX
                z_row.append(format_fraction(-self.c[j], mode=mode))
            else:
                z_row.append(format_fraction(0, mode=mode))
        z_row.append(format_fraction(self.z0, mode=mode))
        
        # Filas de restricciones: x_Bi - sum(d_ij * x_Nj) = b_i
        matrix_rows = []
        for i, b_var in enumerate(self.basic_vars):
            r = []
            for v in all_vars:
                if v in self.non_basic_vars:
                    j = self.non_basic_vars.index(v)
                    # a_ij = -d_ij
                    r.append(format_fraction(-self.d[i][j], mode=mode))
                elif v == b_var:
                    r.append(format_fraction(1, mode=mode))
                else:
                    r.append(format_fraction(0, mode=mode))
            r.append(format_fraction(self.b[i], mode=mode))
            matrix_rows.append({"var": b_var, "row": r})

        return {
            "headers": headers,
            "z_row": z_row,
            "rows": matrix_rows
        }


class StepRecord:
    """
    Registra toda la información detallada de una iteración del Método Simplex Dual.
    """
    def __init__(
        self,
        iteration: int,
        dictionary: Dictionary,
        primal_feasible: bool,
        dual_feasible: bool,
        leaving_var: Optional[str] = None,
        leaving_index: Optional[int] = None,
        entering_var: Optional[str] = None,
        entering_index: Optional[int] = None,
        ratio_tests: Optional[Dict[str, Optional[str]]] = None,
        pivot_element: Optional[str] = None,
        status: str = "IN_PROGRESS",
        explanation: str = ""
    ):
        self.iteration = iteration
        self.dictionary = dictionary.copy()
        self.primal_feasible = primal_feasible
        self.dual_feasible = dual_feasible
        self.leaving_var = leaving_var
        self.leaving_index = leaving_index
        self.entering_var = entering_var
        self.entering_index = entering_index
        self.ratio_tests = ratio_tests or {}
        self.pivot_element = pivot_element
        self.status = status
        self.explanation = explanation

    def to_dict(self, mode: str = "fraction") -> Dict[str, Any]:
        return {
            "iteration": self.iteration,
            "dictionary": self.dictionary.to_dict_repr(mode=mode),
            "tableau": self.dictionary.to_tableau_repr(mode=mode),
            "primal_feasible": self.primal_feasible,
            "dual_feasible": self.dual_feasible,
            "leaving_var": self.leaving_var,
            "leaving_index": self.leaving_index,
            "entering_var": self.entering_var,
            "entering_index": self.entering_index,
            "ratio_tests": self.ratio_tests,
            "pivot_element": self.pivot_element,
            "status": self.status,
            "explanation": self.explanation,
            "primal_solution": {k: format_fraction(v, mode=mode) for k, v in self.dictionary.get_primal_solution().items()},
            "objective_value": format_fraction(self.dictionary.get_objective_value(), mode=mode)
        }


class DualSimplexSolver:
    """
    Solucionador del Método Simplex Dual.
    """
    def __init__(self, dictionary: Dictionary, pivot_rule: str = "bland"):
        """
        pivot_rule: 'bland' (menor índice) o 'most_infeasible' (más negativo).
        """
        self.initial_dictionary = dictionary.copy()
        self.current_dictionary = dictionary.copy()
        self.pivot_rule = pivot_rule.lower()
        self.history: List[StepRecord] = []

    def select_leaving_variable(self) -> Tuple[Optional[int], Optional[str]]:
        """
        Criterio de Salida (Factibilidad Primal):
        Busca las variables básicas con b_i < 0.
        """
        d = self.current_dictionary
        candidates = [(i, d.basic_vars[i], d.b[i]) for i in range(len(d.basic_vars)) if d.b[i] < 0]
        
        if not candidates:
            return None, None

        if self.pivot_rule == "most_infeasible":
            # Elegir el b_i más negativo
            candidates.sort(key=lambda x: x[2])
            return candidates[0][0], candidates[0][1]
        else:
            # Bland's Rule: Elegir la variable con el índice de nombre menor entre las infactibles
            # Extraer número o nombre para ordenar
            candidates.sort(key=lambda x: x[1])
            return candidates[0][0], candidates[0][1]

    def select_entering_variable(self, leaving_idx: int) -> Tuple[Optional[int], Optional[str], Dict[str, Optional[str]]]:
        """
        Criterio de Entrada (Prueba del Cociente Dual para mantener Factibilidad Dual):
        Fila de salida: x_Bk = b_k + sum_j d_{kj} x_Nj
        Buscamos variables no básicas j donde el coeficiente aumentaría x_Bk (es decir d_{kj} > 0).
        (En notación de Tabla Simplex a_{kj} = -d_{kj}, por lo que equivale a a_{kj} < 0).
        
        Para MAX: c_j <= 0.
        El cociente dual es theta_j = | c_j / d_{kj} | = c_j / (-d_{kj}) = -c_j / (-d_{kj}) = c_j / d_{kj} ?
        Veamos con cuidado:
        z' = z0 + c_e x_e + ...
        Al sustituir x_e = (-b_k / d_{ke}) + (1 / d_{ke}) x_Bk - sum_{j!=e} (d_{kj} / d_{ke}) x_Nj:
        El nuevo coef de x_j (j != e) en el objetivo es: c_j' = c_j - c_e * (d_{kj} / d_{ke}).
        Queremos que c_j' <= 0 para todo j.
        Para j tal que d_{kj} > 0:
        c_j - c_e * (d_{kj} / d_{ke}) <= 0
        ==> c_j / d_{kj} <= c_e / d_{ke}.
        Como c_j <= 0 y d_{kj} > 0, el cociente (c_j / d_{kj}) es <= 0.
        Para que c_j' <= 0 se cumpla para TODOS los j con d_{kj} > 0, debemos elegir e que MAXIMICE (c_j / d_{kj}),
        es decir, que MINIMICE | c_j / d_{kj} | = (-c_j / d_{kj}).
        
        Por lo tanto:
        Candidatos: non_basic_vars j con d_{k, j} > 0.
        Ratio = (-c_j) / d_{kj}   (siempre >= 0).
        Elegimos el j con el ratio MÍNIMO.
        """
        d = self.current_dictionary
        ratios: Dict[str, Optional[str]] = {}
        candidates = []

        for j, var_j in enumerate(d.non_basic_vars):
            d_kj = d.d[leaving_idx][j]
            c_j = d.c[j]

            if d_kj > 0:
                # Candidato válido
                # ratio_val = (-c_j) / d_kj (para MAX con c_j <= 0)
                # O si MIN: c_j >= 0, ratio_val = c_j / d_kj
                if d.sense == "MAX":
                    ratio_frac = (-c_j) / d_kj
                else:
                    ratio_frac = c_j / d_kj

                ratios[var_j] = format_fraction(ratio_frac)
                candidates.append((j, var_j, ratio_frac))
            else:
                ratios[var_j] = None  # No elegible (coeficiente d_kj <= 0 no puede ayudar a corregir infactibilidad)

        if not candidates:
            return None, None, ratios

        # En caso de empate en el ratio mínimo, regla de Bland (menor nombre de variable)
        candidates.sort(key=lambda x: (x[2], x[1]))
        entering_idx, entering_var, _ = candidates[0]
        return entering_idx, entering_var, ratios

    def pivot(self, leaving_idx: int, entering_idx: int) -> Dictionary:
        """
        Realiza el pivote entre x_B[leaving_idx] y x_N[entering_idx].
        Actualiza algebraicamente las ecuaciones del diccionario.
        """
        d = self.current_dictionary
        m = len(d.basic_vars)
        n = len(d.non_basic_vars)

        leaving_var = d.basic_vars[leaving_idx]
        entering_var = d.non_basic_vars[entering_idx]

        pivot_coeff = d.d[leaving_idx][entering_idx]  # d_{ke} > 0

        # Crear nuevo diccionario
        new_basic = list(d.basic_vars)
        new_non_basic = list(d.non_basic_vars)
        new_basic[leaving_idx] = entering_var
        new_non_basic[entering_idx] = leaving_var

        new_b = [Fraction(0)] * m
        new_d = [[Fraction(0)] * n for _ in range(m)]
        new_c = [Fraction(0)] * n
        
        # 1. Nueva ecuación para la variable entrante (ahora básica en fila leaving_idx)
        # Ecuación original: x_Bk = b_k + d_{ke} x_Ne + sum_{j != e} d_{kj} x_Nj
        # Despejando x_Ne:
        # x_Ne = (-b_k / d_{ke}) + (1 / d_{ke}) x_Bk - sum_{j != e} (d_{kj} / d_{ke}) x_Nj
        new_b[leaving_idx] = -d.b[leaving_idx] / pivot_coeff
        
        for j in range(n):
            if j == entering_idx:
                # Coeficiente para la variable que sale x_Bk en la nueva posición de x_Ne
                new_d[leaving_idx][j] = Fraction(1) / pivot_coeff
            else:
                new_d[leaving_idx][j] = -d.d[leaving_idx][j] / pivot_coeff

        # 2. Actualizar las demás filas básicas i != leaving_idx
        # x_Bi = b_i + d_{ie} x_Ne + sum_{j != e} d_{ij} x_Nj
        # Sustituyendo x_Ne:
        for i in range(m):
            if i == leaving_idx:
                continue
            d_ie = d.d[i][entering_idx]
            new_b[i] = d.b[i] + d_ie * new_b[leaving_idx]
            for j in range(n):
                if j == entering_idx:
                    new_d[i][j] = d_ie * new_d[leaving_idx][entering_idx]
                else:
                    new_d[i][j] = d.d[i][j] + d_ie * new_d[leaving_idx][j]

        # 3. Actualizar la función objetivo z
        # z = z0 + c_e x_Ne + sum_{j != e} c_j x_Nj
        # Sustituyendo x_Ne:
        c_e = d.c[entering_idx]
        new_z0 = d.z0 + c_e * new_b[leaving_idx]

        for j in range(n):
            if j == entering_idx:
                new_c[j] = c_e * new_d[leaving_idx][entering_idx]
            else:
                new_c[j] = d.c[j] + c_e * new_d[leaving_idx][j]

        return Dictionary(
            basic_vars=new_basic,
            non_basic_vars=new_non_basic,
            b=new_b,
            d=new_d,
            c=new_c,
            z0=new_z0,
            sense=d.sense
        )

    def solve(self, max_iterations: int = 100) -> List[StepRecord]:
        """
        Ejecuta iterativamente el algoritmo Simplex Dual hasta encontrar la solución óptima,
        detectar infactibilidad primal (dual no acotado) o sobrepasar max_iterations.
        """
        self.history = []
        iteration = 0

        # Verificación inicial de factibilidad dual
        if not self.current_dictionary.is_dual_feasible():
            rec = StepRecord(
                iteration=iteration,
                dictionary=self.current_dictionary,
                primal_feasible=self.current_dictionary.is_primal_feasible(),
                dual_feasible=False,
                status="NOT_DUAL_FEASIBLE",
                explanation="El diccionario inicial NO es dual-factible. El Método Simplex Dual requiere un punto inicial dual-factible (coeficientes en z <= 0 para Max)."
            )
            self.history.append(rec)
            return self.history

        while iteration < max_iterations:
            dict_curr = self.current_dictionary
            primal_feas = dict_curr.is_primal_feasible()
            dual_feas = dict_curr.is_dual_feasible()

            # Caso de parada 1: Factibilidad Primal alcanzada -> SOLUCIÓN ÓPTIMA
            if primal_feas:
                rec = StepRecord(
                    iteration=iteration,
                    dictionary=dict_curr,
                    primal_feasible=True,
                    dual_feasible=True,
                    status="OPTIMAL",
                    explanation="¡Solución Óptima Encontrada! Todas las variables básicas son no negativas (b_i >= 0) y el diccionario mantiene factibilidad dual."
                )
                self.history.append(rec)
                break

            # Criterio de Salida: Seleccionar variable básica infactible (b_i < 0)
            leaving_idx, leaving_var = self.select_leaving_variable()
            if leaving_idx is None:
                # No hay b_i < 0 (no debería ocurrir tras primal_feas check)
                break

            # Criterio de Entrada: Test del Cociente Dual
            entering_idx, entering_var, ratio_tests = self.select_entering_variable(leaving_idx)

            # Caso de parada 2: No hay variable no básica con coef d_{kj} > 0 -> PROBLEMA INFACTIBLE
            if entering_idx is None:
                pivot_elem_str = None
                rec = StepRecord(
                    iteration=iteration,
                    dictionary=dict_curr,
                    primal_feasible=False,
                    dual_feasible=True,
                    leaving_var=leaving_var,
                    leaving_index=leaving_idx,
                    ratio_tests=ratio_tests,
                    status="INFEASIBLE",
                    explanation=f"¡Problema Infactible! La variable de salida '{leaving_var}' tiene b_{leaving_idx+1} < 0, pero ningún coeficiente de variable no básica en su fila es positivo (d_{{{leaving_var}, j}} <= 0). El problema dual es no acotado."
                )
                self.history.append(rec)
                break

            # Elemento Pivote d_{ke}
            pivot_val = dict_curr.d[leaving_idx][entering_idx]
            pivot_elem_str = f"d({leaving_var}, {entering_var}) = {format_fraction(pivot_val)}"

            # Explicación detallada del paso
            exp = (
                f"Iteración {iteration + 1}:\n"
                f"- Variable que sale: {leaving_var} (b_{leaving_var} = {format_fraction(dict_curr.b[leaving_idx])} < 0).\n"
                f"- Test del cociente dual: min {{ |c_j / d_{{{leaving_var}, j}}| : d_{{{leaving_var}, j}} > 0 }}.\n"
                f"- Variable que entra: {entering_var} (con cociente dual mínimo = {ratio_tests.get(entering_var)}).\n"
                f"- Pivote: Intercambio de {leaving_var} y {entering_var} con d = {format_fraction(pivot_val)}."
            )

            rec = StepRecord(
                iteration=iteration,
                dictionary=dict_curr,
                primal_feasible=False,
                dual_feasible=True,
                leaving_var=leaving_var,
                leaving_index=leaving_idx,
                entering_var=entering_var,
                entering_index=entering_idx,
                ratio_tests=ratio_tests,
                pivot_element=pivot_elem_str,
                status="IN_PROGRESS",
                explanation=exp
            )
            self.history.append(rec)

            # Realizar Pivote y actualizar diccionario
            self.current_dictionary = self.pivot(leaving_idx, entering_idx)
            iteration += 1

        if iteration >= max_iterations and self.history and self.history[-1].status == "IN_PROGRESS":
            rec = StepRecord(
                iteration=iteration,
                dictionary=self.current_dictionary,
                primal_feasible=self.current_dictionary.is_primal_feasible(),
                dual_feasible=self.current_dictionary.is_dual_feasible(),
                status="MAX_ITERATIONS_REACHED",
                explanation=f"Se alcanzó el límite máximo de iteraciones ({max_iterations}). Es posible que exista un ciclo de degeneración."
            )
            self.history.append(rec)

        return self.history
