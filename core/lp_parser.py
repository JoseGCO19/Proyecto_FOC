import json
import re
from fractions import Fraction
from typing import Dict, List, Tuple, Any, Optional
from core.fraction_utils import parse_number
from core.dual_simplex import Dictionary

class LPParser:
    """
    Parser universal de Problemas de Programación Lineal (PL).
    Soporta formato Matricial (JSON / Dict) y Sintaxis Algebraica en Texto.
    """
    
    @staticmethod
    def from_json_dict(data: Dict[str, Any]) -> Dictionary:
        """
        Crea un Diccionario Simplex inicial a partir de una estructura JSON/Dict.
        """
        sense = data.get("sense", "MAX").upper()
        c_raw = data.get("c", [])
        A_raw = data.get("A", [])
        b_raw = data.get("b", [])
        ops = data.get("ops", ["<="] * len(b_raw))
        var_names = data.get("var_names", [f"x{j+1}" for j in range(len(c_raw))])

        m = len(A_raw)
        n = len(c_raw)

        c_frac = [parse_number(val) for val in c_raw]
        A_frac = [[parse_number(val) for val in row] for row in A_raw]
        b_frac = [parse_number(val) for val in b_raw]

        basic_vars = []
        non_basic_vars = list(var_names)
        
        b_dict = []
        d_dict = []

        slack_count = 1
        for i in range(m):
            op = ops[i] if i < len(ops) else "<="
            row_A = A_frac[i]
            val_b = b_frac[i]
            
            s_name = f"s{slack_count}"
            slack_count += 1
            basic_vars.append(s_name)

            if op == "<=":
                b_dict.append(val_b)
                d_dict.append([-val for val in row_A])
            elif op == ">=":
                b_dict.append(-val_b)
                d_dict.append([val for val in row_A])
            else:
                # Igualdad '='
                b_dict.append(val_b)
                d_dict.append([-val for val in row_A])

        z0_frac = parse_number(data.get("z0", 0))

        return Dictionary(
            basic_vars=basic_vars,
            non_basic_vars=non_basic_vars,
            b=b_dict,
            d=d_dict,
            c=c_frac,
            z0=z0_frac,
            sense=sense
        )

    @staticmethod
    def from_file(file_path: str) -> Dictionary:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            
        if file_path.endswith(".json") or content.startswith("{"):
            return LPParser.from_json_dict(json.loads(content))
        else:
            return LPParser.parse_text_algebraic(content)

    @staticmethod
    def parse_text_algebraic(text: str) -> Dictionary:
        lines = [line.strip() for line in text.strip().split("\n") if line.strip() and not line.strip().startswith("#")]
        
        sense = "MAX"
        obj_line = ""
        constraint_lines = []
        is_st = False

        for line in lines:
            upper_l = line.upper()
            if upper_l.startswith("MAX") or upper_l.startswith("MIN"):
                obj_line = line
            elif "S.T." in upper_l or "SUBJECT TO" in upper_l or "RESTRICCIONES" in upper_l:
                is_st = True
            elif is_st:
                # Omitir líneas de no negatividad como x1, x2 >= 0 o x1,x2>=0
                clean_l = line.replace(" ", "")
                if ">=" in clean_l and clean_l.endswith("0") and ("," in clean_l or clean_l.startswith("x") or clean_l.startswith("s")):
                    # Si no contiene operadores de suma/resta antes de >=, es no-negatividad
                    lhs = clean_l.split(">=")[0]
                    if not any(char in lhs for char in ["+", "-", "*"]):
                        continue
                constraint_lines.append(line)

        if not obj_line:
            raise ValueError("No se encontró la línea de Función Objetivo (MAX o MIN).")

        if obj_line.upper().startswith("MIN"):
            sense = "MIN"
        
        obj_expr = re.sub(r'^(MAX|MIN)\s*(z\s*=)?', '', obj_line, flags=re.IGNORECASE).strip()
        
        # Encontrar todas las variables
        var_set = set()
        for text_chunk in [obj_expr] + constraint_lines:
            matches = re.findall(r'\b([a-zA-Z][a-zA-Z0-9_]*)\b', text_chunk)
            for v in matches:
                if v.upper() not in ["MAX", "MIN", "ST", "SUBJECT", "TO", "Z"]:
                    var_set.add(v)

        def var_key(v_name: str):
            digits = re.findall(r'\d+', v_name)
            prefix = re.sub(r'\d+', '', v_name)
            return (prefix, int(digits[0]) if digits else 0)

        var_names = sorted(list(var_set), key=var_key)
        
        c_dict = LPParser._parse_linear_expression(obj_expr, var_names)
        c_vec = [c_dict.get(v, Fraction(0)) for v in var_names]

        A_matrix = []
        b_vector = []
        ops_list = []

        for c_line in constraint_lines:
            op_match = re.search(r'(<=|>=|=)', c_line)
            if not op_match:
                continue
            op = op_match.group(1)
            lhs_str, rhs_str = c_line.split(op, 1)
            
            row_coeffs = LPParser._parse_linear_expression(lhs_str, var_names)
            rhs_val = parse_number(rhs_str.strip())

            A_matrix.append([row_coeffs.get(v, Fraction(0)) for v in var_names])
            b_vector.append(rhs_val)
            ops_list.append(op)

        return LPParser.from_json_dict({
            "sense": sense,
            "c": c_vec,
            "A": A_matrix,
            "b": b_vector,
            "ops": ops_list,
            "var_names": var_names
        })

    @staticmethod
    def _parse_linear_expression(expr: str, var_names: List[str]) -> Dict[str, Fraction]:
        """
        Extrae los coeficientes numéricos de las variables especificadas.
        Soporta expresiones como: '-3x1 + 5x2 - 4/3 x3' o '2 x1 + x2'.
        """
        coeffs: Dict[str, Fraction] = {v: Fraction(0) for v in var_names}
        
        # Regex para buscar patrones: [signo][numero/fraccion]?[espacio]*[nombre_variable]
        for v in var_names:
            # Coincidencias con la variable v
            pattern = r'([+-]?\s*\d*(?:\.\d+)?(?:/\d+)?)\s*\*?\s*\b' + re.escape(v) + r'\b'
            matches = re.findall(pattern, expr)
            for m in matches:
                m_str = m.replace(" ", "").strip()
                if not m_str or m_str == "+":
                    val = Fraction(1)
                elif m_str == "-":
                    val = Fraction(-1)
                else:
                    val = parse_number(m_str)
                coeffs[v] += val

        return coeffs
