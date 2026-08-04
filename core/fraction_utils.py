from fractions import Fraction
from typing import Union, List, Any

def parse_number(val: Any) -> Fraction:
    """
    Convierte enteros, flotantes, cadenas ('3/4', '-0.5', '7') o Fractions a Fraction.
    """
    if isinstance(val, Fraction):
        return val
    if isinstance(val, (int, bool)):
        return Fraction(int(val), 1)
    if isinstance(val, float):
        # Evita imprecisiones de flotantes convirtiendo via str
        return Fraction(str(val))
    if isinstance(val, str):
        val_str = val.strip().replace(" ", "")
        if "/" in val_str:
            parts = val_str.split("/")
            if len(parts) == 2:
                return Fraction(int(parts[0]), int(parts[1]))
        elif "." in val_str:
            return Fraction(val_str)
        else:
            return Fraction(int(val_str), 1)
    raise ValueError(f"No se pudo convertir '{val}' de tipo {type(val)} a Fraction.")

def format_fraction(val: Union[Fraction, int, float], mode: str = "fraction", decimals: int = 4) -> str:
    """
    Formatea un valor numérico como Fracción exacta ('3/4'), Entero ('5') o Decimal ('0.75').
    mode: 'fraction' | 'decimal' | 'latex'
    """
    frac = parse_number(val) if not isinstance(val, Fraction) else val
    
    if mode == "decimal":
        flt = float(frac)
        if flt.is_integer():
            return str(int(flt))
        return f"{flt:.{decimals}f}".rstrip('0').rstrip('.')

    # Fracción / Latex
    if frac.denominator == 1:
        return str(frac.numerator)
    
    if mode == "latex":
        if frac.numerator < 0:
            return f"-\\frac{{{-frac.numerator}}}{{{frac.denominator}}}"
        return f"\\frac{{{frac.numerator}}}{{{frac.denominator}}}"
    
    return f"{frac.numerator}/{frac.denominator}"

def format_vector(vec: List[Any], mode: str = "fraction", decimals: int = 4) -> List[str]:
    return [format_fraction(x, mode=mode, decimals=decimals) for x in vec]

def format_matrix(mat: List[List[Any]], mode: str = "fraction", decimals: int = 4) -> List[List[str]]:
    return [format_vector(row, mode=mode, decimals=decimals) for row in mat]
