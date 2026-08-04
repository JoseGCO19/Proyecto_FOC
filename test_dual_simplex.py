import unittest
from fractions import Fraction
from core.fraction_utils import parse_number, format_fraction
from core.dual_simplex import Dictionary, DualSimplexSolver
from core.lp_parser import LPParser

class TestDualSimplex(unittest.TestCase):

    def test_fraction_utils(self):
        self.assertEqual(parse_number("3/4"), Fraction(3, 4))
        self.assertEqual(parse_number("-0.5"), Fraction(-1, 2))
        self.assertEqual(parse_number(5), Fraction(5, 1))
        self.assertEqual(format_fraction(Fraction(3, 4), mode="fraction"), "3/4")
        self.assertEqual(format_fraction(Fraction(-1, 2), mode="latex"), "-\\frac{1}{2}")
        self.assertEqual(format_fraction(Fraction(4, 2), mode="fraction"), "2")

    def test_dual_simplex_standard_problem(self):
        """
        Ejemplo Estándar Simplex Dual:
        Minimizar z = 3x1 + 2x2
        s.t.
        x1 + 2x2 >= 6  => -x1 - 2x2 <= -6  => s1 = -6 + x1 + 2x2
        2x1 + x2 >= 8  => -2x1 - x2 <= -8  => s2 = -8 + 2x1 + x2
        x1, x2 >= 0
        
        Maximización equivalente:
        Max z = -3x1 - 2x2 (dual factible c = [-3, -2] <= 0)
        """
        dict_init = Dictionary(
            basic_vars=["s1", "s2"],
            non_basic_vars=["x1", "x2"],
            b=[-6, -8],
            d=[
                [1, 2],
                [2, 1]
            ],
            c=[-3, -2],
            z0=0,
            sense="MAX"
        )

        solver = DualSimplexSolver(dict_init, pivot_rule="bland")
        history = solver.solve()

        final_step = history[-1]
        self.assertEqual(final_step.status, "OPTIMAL")
        self.assertTrue(final_step.primal_feasible)
        
        sol = final_step.dictionary.get_primal_solution()
        self.assertEqual(sol["x1"], Fraction(10, 3))
        self.assertEqual(sol["x2"], Fraction(4, 3))
        self.assertEqual(final_step.dictionary.get_objective_value(), Fraction(-38, 3))

    def test_dual_simplex_infeasible_problem(self):
        """
        Problema Infactible (Dual no acotado):
        Max z = -x1 - x2
        s.t.
        -x1 - x2 <= -5  => s1 = -5 + x1 + x2
        x1 + x2 <= 2    => s2 = 2 - x1 - x2
        """
        dict_init = Dictionary(
            basic_vars=["s1", "s2"],
            non_basic_vars=["x1", "x2"],
            b=[-5, 2],
            d=[
                [1, 1],
                [-1, -1]
            ],
            c=[-1, -1],
            z0=0,
            sense="MAX"
        )

        solver = DualSimplexSolver(dict_init)
        history = solver.solve()

        final_step = history[-1]
        self.assertIn(final_step.status, ["INFEASIBLE", "OPTIMAL"])
        if final_step.status != "INFEASIBLE":
            self.assertTrue(any(h.status == "INFEASIBLE" for h in history))

    def test_lp_parser_algebraic(self):
        text = """
        MAX z = -3 x1 - 5 x2
        s.t.
        x1 + 2 x2 >= 6
        3 x1 + 2 x2 >= 12
        x1, x2 >= 0
        """
        d = LPParser.parse_text_algebraic(text)
        self.assertEqual(d.non_basic_vars, ["x1", "x2"])
        self.assertEqual(d.basic_vars, ["s1", "s2"])
        self.assertEqual(d.b, [Fraction(-6), Fraction(-12)])
        self.assertEqual(d.c, [Fraction(-3), Fraction(-5)])
        self.assertEqual(d.d, [[Fraction(1), Fraction(2)], [Fraction(3), Fraction(2)]])

    def test_lp_parser_json(self):
        json_data = {
            "sense": "MAX",
            "c": [-2, -3],
            "A": [[-1, -1], [-2, -1]],
            "b": [-4, -6],
            "var_names": ["x1", "x2"]
        }
        d = LPParser.from_json_dict(json_data)
        self.assertEqual(d.b, [Fraction(-4), Fraction(-6)])
        self.assertEqual(d.d, [[Fraction(1), Fraction(1)], [Fraction(2), Fraction(1)]])

if __name__ == "__main__":
    unittest.main()
