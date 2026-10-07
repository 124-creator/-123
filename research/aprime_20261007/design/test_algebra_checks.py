"""Pure rational algebra checks; no price data and no model training."""
import json
from fractions import Fraction as F
from pathlib import Path
import subprocess
import sys
import unittest

try:
    import algebra_checks as ac
except ModuleNotFoundError as exc:
    if exc.name != "algebra_checks":
        raise
    ac = None


class AlgebraChecks(unittest.TestCase):
    def require(self, name):
        fn = getattr(ac, name, None)
        self.assertTrue(callable(fn), "Missing behavior: " + name)
        return fn

    def test_price_decomposition_reconstructs_exactly(self):
        basis = self.require("decompose_price")
        for price, composite in ((F(7, 3), F(-5, 2)), (F(0), F(4, 7)), (F(-8), F(9))):
            self.assertEqual(composite + basis(price, composite), price)

    def test_rw_plus_constant_basis_is_annual_rw(self):
        forecast = self.require("rw_plus_constant_basis")
        for last_p, last_c in ((F(11, 5), F(7, 3)), (F(-2), F(4))):
            last_b = ac.decompose_price(last_p, last_c)
            self.assertEqual(forecast(last_c, last_b), last_p)

    def test_same_fixed_operator_is_additive(self):
        linear = self.require("apply_linear")
        operator = ((F(2, 3), F(-5, 7), F(0)), (F(-1), F(4), F(1, 9)))
        # All basis-vector pairs check columns; fractions add an exact witness.
        vectors = [(F(1), F(0), F(0)), (F(0), F(1), F(0)),
                   (F(0), F(0), F(1)), (F(3, 7), F(-2, 5), F(11, 13))]
        for c in vectors:
            for b in vectors:
                p = tuple(ci + bi for ci, bi in zip(c, b))
                summed = tuple(ci + bi for ci, bi in zip(linear(operator, c), linear(operator, b)))
                self.assertEqual(summed, linear(operator, p))

    def test_linear_rejects_empty_operator(self):
        with self.assertRaises(ValueError):
            ac.apply_linear((), (F(1),))

    def test_linear_rejects_ragged_operator(self):
        with self.assertRaises(ValueError):
            ac.apply_linear(((1, 2), (3,)), (F(1), F(1)))

    def test_linear_rejects_vector_dimension_mismatch(self):
        for vector in ((), (F(1),), (F(1), F(2), F(3))):
            with self.assertRaises(ValueError):
                ac.apply_linear(((F(1), F(2)),), vector)

    def test_exact_domain_rejects_float_bool_string(self):
        for invalid in (0.5, True, "1/2"):
            with self.subTest(invalid=invalid):
                with self.assertRaises(TypeError):
                    ac.decompose_price(invalid, F(1))
                with self.assertRaises(TypeError):
                    ac.rw_plus_constant_basis(F(1), invalid)
                with self.assertRaises(TypeError):
                    ac.apply_linear(((F(1),),), (invalid,))
                with self.assertRaises(TypeError):
                    ac.apply_linear(((invalid,),), (F(1),))

    def test_same_lambda_ridge_operator_is_exactly_additive(self):
        ridge = self.require("ridge_operator")
        x = ((1, 0), (1, 1), (1, 2))
        operator = ridge(x, F(2))
        expected = ((F(7, 26), F(2, 13), F(1, 26)),
                    (F(-3, 26), F(1, 13), F(7, 26)))
        self.assertEqual(operator, expected)
        # Exact normal-equation identity: (X'X+2I)A=X'.
        gram = ((5, 3), (3, 7))
        for row in range(2):
            for col in range(3):
                self.assertEqual(sum(gram[row][k]*operator[k][col] for k in range(2)), x[col][row])
        c, b = (F(1, 3), F(-2), F(5, 7)), (F(-1), F(4, 5), F(2))
        p = tuple(ci+bi for ci,bi in zip(c,b))
        self.assertEqual(tuple(ci+bi for ci,bi in zip(ac.apply_linear(operator,c),ac.apply_linear(operator,b))),
                         ac.apply_linear(operator,p))

    def test_zero_lambda_is_exact_ols_operator(self):
        fn = self.require("ols_operator")
        x = ((1, 0), (1, 1), (1, 2))
        expected = ((F(5, 6), F(1, 3), F(-1, 6)), (F(-1, 2), F(0), F(1, 2)))
        self.assertEqual(fn(x), expected)
        self.assertEqual(fn(x), ac.ridge_operator(x, F(0)))
        c, b = (F(2, 3), F(5), F(-2)), (F(1), F(-1, 7), F(9))
        p = tuple(ci+bi for ci,bi in zip(c,b))
        self.assertEqual(tuple(ci+bi for ci,bi in zip(ac.apply_linear(fn(x),c),ac.apply_linear(fn(x),b))),
                         ac.apply_linear(fn(x),p))

    def test_ridge_rejects_negative_lambda(self):
        with self.assertRaises(ValueError):
            ac.ridge_operator(((1, 0), (1, 1)), F(-1, 10))

    def test_singular_design_is_explicit_value_error(self):
        try:
            ac.ols_operator(((1, 1), (2, 2)))
        except Exception as exc:
            self.assertIsInstance(exc, ValueError, "singularity requires an explicit ValueError")
        else:
            self.fail("singular design was accepted")

    def test_common_unpenalized_intercept_ridge_is_additive(self):
        import inspect
        self.assertIn("penalty", inspect.signature(ac.ridge_operator).parameters,
                      "Missing common intercept penalty mask")
        x = ((1, 0), (1, 1), (1, 2))
        operator = ac.ridge_operator(x, F(2), penalty=(0, 1))
        expected = ((F(7, 12), F(1, 3), F(1, 12)), (F(-1, 4), F(0), F(1, 4)))
        self.assertEqual(operator, expected)
        c, b = (F(2), F(-3), F(7, 2)), (F(4, 5), F(8), F(-1))
        p = tuple(ci+bi for ci,bi in zip(c,b))
        self.assertEqual(tuple(ci+bi for ci,bi in zip(ac.apply_linear(operator,c),ac.apply_linear(operator,b))),
                         ac.apply_linear(operator,p))

    def test_ridge_rejects_penalty_dimension_mismatch(self):
        for penalty in ((), (1,), (1, 1, 1)):
            try:
                ac.ridge_operator(((1, 0), (1, 1)), F(1), penalty=penalty)
            except Exception as exc:
                self.assertIsInstance(exc, ValueError, "penalty dimensions require ValueError")
            else:
                self.fail("penalty dimension mismatch was accepted")

    def test_ridge_rejects_negative_penalty(self):
        with self.assertRaises(ValueError):
            ac.ridge_operator(((1, 0), (1, 1)), F(1, 10), penalty=(0, -1))

    def test_different_fixed_operators_need_not_be_equivalent(self):
        gap = self.require("equivalence_gap")
        c, b = (F(1), F(2)), (F(3), F(4))
        common = ((F(1), F(0)),)
        different = ((F(0), F(1)),)
        self.assertEqual(gap(common, common, common, c, b), (F(0),))
        self.assertEqual(gap(common, different, common, c, b), (F(1),))
        # Different regularization: same X, but lambda_C != lambda_B.
        x = ((1,), (2,))
        a0, a1 = ac.ridge_operator(x, F(0)), ac.ridge_operator(x, F(1))
        self.assertNotEqual(gap(a0, a1, a0, c, b), (F(0),))

    def test_gap_rejects_unaligned_shapes(self):
        with self.assertRaises(ValueError):
            ac.equivalence_gap(((1,),), ((1,), (2,)), ((1,),), (F(1),), (F(2),))
        with self.assertRaises(ValueError):
            ac.equivalence_gap(((1,),), ((1, 0),), ((1,),), (F(1),), (F(2), F(3)))

    def test_nonadditive_postprocessing_breaks_equivalence(self):
        import inspect
        self.assertIn("postprocess", inspect.signature(ac.equivalence_gap).parameters,
                      "Missing postprocessing comparison")
        operator = ((F(1),),)
        c, b = (F(-1),), (F(2),)
        clip = lambda value: max(F(0), value)
        self.assertEqual(ac.equivalence_gap(operator, operator, operator, c, b), (F(0),))
        self.assertEqual(ac.equivalence_gap(operator, operator, operator, c, b, postprocess=clip), (F(1),))
        self.assertEqual(ac.equivalence_gap(operator, operator, operator, c, b, postprocess=lambda v: v+1), (F(1),))

    def test_covariance_controls_composite_error_variance(self):
        variance = self.require("combined_error_variance")
        self.assertEqual(variance(F(4), F(9), F(0)), F(13))
        self.assertEqual(variance(F(4), F(9), F(6)), F(25))
        self.assertEqual(variance(F(4), F(9), F(-6)), F(1))
        self.assertEqual(variance(F(0), F(0), F(0)), F(0))

    def test_error_variance_rejects_negative_marginal_variance(self):
        for var_c, var_b in ((F(-1), F(1)), (F(1), F(-1))):
            with self.assertRaises(ValueError):
                ac.combined_error_variance(var_c, var_b, F(0))

    def test_error_variance_rejects_impossible_covariance(self):
        for var_c, var_b, cov in ((F(4), F(9), F(7)), (F(4), F(9), F(-7)), (F(0), F(1), F(1))):
            with self.assertRaises(ValueError):
                ac.combined_error_variance(var_c, var_b, cov)

    def test_marginal_endpoints_do_not_preserve_joint_coverage(self):
        coverages = self.require("finite_interval_coverages")
        atoms = ((F(9, 10), F(0), F(0)), (F(1, 20), F(2), F(0)),
                 (F(1, 20), F(0), F(2)))
        result = coverages(atoms, (F(0), F(1, 2)), (F(0), F(1, 2)))
        self.assertEqual(result["marginal_c"], F(19, 20))
        self.assertEqual(result["marginal_b"], F(19, 20))
        self.assertEqual(result["joint_rectangle"], F(9, 10))
        self.assertEqual(result["sum_endpoints"], F(9, 10))
        self.assertLess(result["sum_endpoints"], result["marginal_c"])

    def test_interval_law_requires_unit_total_mass(self):
        for atoms in ((), ((F(1, 2), F(0), F(0)),), ((F(2), F(0), F(0)),)):
            with self.assertRaises(ValueError):
                ac.finite_interval_coverages(atoms, (0, 1), (0, 1))

    def test_interval_law_rejects_negative_mass(self):
        atoms = ((F(-1), F(0), F(0)), (F(2), F(1), F(1)))
        with self.assertRaises(ValueError):
            ac.finite_interval_coverages(atoms, (0, 1), (0, 1))

    def test_interval_bounds_must_be_ordered(self):
        atoms = ((F(1), F(0), F(0)),)
        for interval_c, interval_b in (((1, 0), (0, 1)), ((0, 1), (1, 0))):
            with self.assertRaises(ValueError):
                ac.finite_interval_coverages(atoms, interval_c, interval_b)

    def test_interval_law_rejects_malformed_atom(self):
        for atoms in (((),), ((F(1), F(0)),), ((F(1), F(0), F(0), F(0)),)):
            try:
                ac.finite_interval_coverages(atoms, (0, 1), (0, 1))
            except Exception as exc:
                self.assertIsInstance(exc, ValueError, "atom structure requires ValueError")
            else:
                self.fail("malformed atom was accepted")

    def test_report_contains_only_scoped_algebra_results(self):
        report = self.require("build_report")()
        self.assertEqual(report["scope"], "pure_algebra_no_price_data_no_training")
        self.assertTrue(report["all_passed"])
        self.assertTrue(report["not_evidence_of_predictive_gain"])
        for name in ("decomposition", "rw_identity", "fixed_operator", "ols_same_design_fitted",
                     "ridge_same_lambda_fitted", "common_xstar_forecast", "different_operator_counterexample",
                     "postprocess_counterexample", "covariance_effect", "interval_counterexample"):
            self.assertIs(report["checks"][name], True)
        self.assertEqual(report["interval_counterexample"]["sum_endpoints"], "9/10")
        self.assertNotIn("rmse", report)
        self.assertNotIn("carbon_prices", report)

    def test_cli_emits_scoped_report_in_both_interpreter_modes(self):
        script = Path(__file__).with_name("algebra_checks.py")
        for flags in ((), ("-O",)):
            run = subprocess.run([sys.executable, "-B", *flags, str(script)],
                                 capture_output=True, text=True, check=False)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertTrue(run.stdout.strip(), "Missing CLI report")
            self.assertEqual(json.loads(run.stdout), ac.build_report())
            self.assertEqual(run.stderr, "")

    def test_mean_additivity_does_not_imply_median_additivity(self):
        functionals = self.require("finite_point_functionals")
        atoms = ((F(2, 5), F(0), F(1)), (F(2, 5), F(1), F(0)),
                 (F(1, 5), F(0), F(0)))
        result = functionals(atoms, F(1, 2))
        self.assertEqual(result["mean_c"], F(2, 5))
        self.assertEqual(result["mean_b"], F(2, 5))
        self.assertEqual(result["mean_p"], F(4, 5))
        self.assertEqual(result["mean_c"] + result["mean_b"], result["mean_p"])
        self.assertEqual(result["quantile_c"], F(0))
        self.assertEqual(result["quantile_b"], F(0))
        self.assertEqual(result["quantile_p"], F(1))
        self.assertNotEqual(result["quantile_c"]+result["quantile_b"], result["quantile_p"])

    def test_point_functional_requires_valid_quantile_level(self):
        atoms = ((F(1), F(0), F(1)),)
        for level in (F(0), F(-1, 10), F(11, 10)):
            with self.assertRaises(ValueError):
                ac.finite_point_functionals(atoms, level)

    def test_report_exposes_mean_vs_median_counterexample(self):
        report = ac.build_report()
        self.assertIn("conditional_mean_additivity", report["checks"], "Missing mean/median distinction")
        self.assertTrue(report["checks"]["conditional_mean_additivity"])
        self.assertTrue(report["checks"]["median_nonadditivity"])
        fixture = report["point_functional_fixture"]
        self.assertEqual(fixture["mean_p"], "4/5")
        self.assertEqual(fixture["quantile_c"], "0")
        self.assertEqual(fixture["quantile_b"], "0")
        self.assertEqual(fixture["quantile_p"], "1")

# TESTS_END

if __name__ == "__main__":
    unittest.main()
