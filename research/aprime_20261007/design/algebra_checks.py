"""Exact algebra only. All inputs are synthetic rational coefficients.
No external data, model training, statistical performance or trading output.
"""
from fractions import Fraction
import json

def decompose_price(price, composite):
    """Return B=P-C; scalars denote abstract coefficients, not observations."""
    return _exact(price) - _exact(composite)


def rw_plus_constant_basis(composite_last, basis_last):
    """RW(C) + unchanged B at any horizon; same last timestamp is assumed."""
    return _exact(composite_last) + _exact(basis_last)


def apply_linear(operator, vector):
    """Apply one fixed operator without estimating coefficients from targets."""
    operator = tuple(tuple(row) for row in operator)
    if not operator or not operator[0]:
        raise ValueError("operator must be nonempty")
    if any(len(row) != len(operator[0]) for row in operator):
        raise ValueError("operator must be rectangular")
    vector = tuple(vector)
    if len(vector) != len(operator[0]):
        raise ValueError("operator/vector dimension mismatch")
    return tuple(sum((_exact(a) * _exact(b) for a, b in zip(row, vector)), Fraction(0))
                 for row in operator)


def _exact(value):
    """Only explicit rational scalars; bool, floats and strings are not accepted."""
    if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
        raise TypeError("exact int or Fraction required")
    return Fraction(value)


def ridge_operator(design, lam, penalty=None):
    """Build A=(X'X+lambda diag(penalty))^-1 X'; no target is fitted."""
    x = tuple(tuple(_exact(value) for value in row) for row in design)
    width = len(x[0]) if x else 0
    apply_linear(x, (0,) * width)
    lam = _exact(lam)
    if lam < 0:
        raise ValueError("lambda must be nonnegative")
    penalty = (Fraction(1),) * width if penalty is None else tuple(_exact(v) for v in penalty)
    if len(penalty) != width:
        raise ValueError("penalty dimension mismatch")
    if any(value < 0 for value in penalty):
        raise ValueError("penalty weights must be nonnegative")
    gram = [[sum((row[i] * row[j] for row in x), Fraction(0))
             + (lam * penalty[i] if i == j else 0) for j in range(width)] for i in range(width)]
    augmented = [row + [Fraction(int(i == j)) for j in range(width)]
                 for i, row in enumerate(gram)]
    for col in range(width):
        pivot = next((i for i in range(col, width) if augmented[i][col]), None)
        if pivot is None:
            raise ValueError("singular coefficient matrix; common fixed pseudoinverse not implemented")
        augmented[col], augmented[pivot] = augmented[pivot], augmented[col]
        scale = augmented[col][col]
        augmented[col] = [value / scale for value in augmented[col]]
        for i in range(width):
            if i != col:
                scale = augmented[i][col]
                augmented[i] = [a - scale * b for a, b in zip(augmented[i], augmented[col])]
    inverse = [row[width:] for row in augmented]
    return tuple(tuple(sum((inverse[i][j] * row[j] for j in range(width)), Fraction(0))
                       for row in x) for i in range(width))


def ols_operator(design):
    """OLS coefficient map at fixed X, without any observed response vector."""
    return ridge_operator(design, Fraction(0))


def equivalence_gap(operator_c, operator_b, operator_p, c, b, postprocess=None):
    """Return split-minus-direct for explicit possibly different operators."""
    c, b = tuple(c), tuple(b)
    if len(c) != len(b):
        raise ValueError("C and B must have the same aligned length")
    p = tuple(_exact(ci) + _exact(bi) for ci, bi in zip(c, b))
    fitted_c = apply_linear(operator_c, c)
    fitted_b = apply_linear(operator_b, b)
    fitted_p = apply_linear(operator_p, p)
    if not len(fitted_c) == len(fitted_b) == len(fitted_p):
        raise ValueError("output shapes must match")
    if postprocess is not None:
        fitted_c = tuple(_exact(postprocess(value)) for value in fitted_c)
        fitted_b = tuple(_exact(postprocess(value)) for value in fitted_b)
        fitted_p = tuple(_exact(postprocess(value)) for value in fitted_p)
    return tuple(ci + bi - pi for ci, bi, pi in zip(fitted_c, fitted_b, fitted_p))


def combined_error_variance(var_c, var_b, covariance):
    """Var(e_C+e_B), not marginal interval width or empirical performance."""
    var_c, var_b, covariance = _exact(var_c), _exact(var_b), _exact(covariance)
    if var_c < 0 or var_b < 0:
        raise ValueError("variances must be nonnegative")
    if covariance * covariance > var_c * var_b:
        raise ValueError("covariance matrix must be positive semidefinite")
    return var_c + var_b + 2 * covariance


def finite_interval_coverages(atoms, interval_c, interval_b):
    """Exact event masses of a stated finite joint law, not fitted coverage.

    atoms contain (mass, C, B); endpoints are closed. Summing endpoints is
    evaluated as a set construction, never assigned a nominal joint level.
    """
    lo_c, hi_c = tuple(_exact(value) for value in interval_c)
    lo_b, hi_b = tuple(_exact(value) for value in interval_b)
    if lo_c > hi_c or lo_b > hi_b:
        raise ValueError("interval lower endpoint exceeds upper endpoint")
    atoms = _joint_atoms(atoms)
    result = {name: Fraction(0) for name in
              ("marginal_c", "marginal_b", "joint_rectangle", "sum_endpoints")}
    for mass, c, b in atoms:
        inside_c, inside_b = lo_c <= c <= hi_c, lo_b <= b <= hi_b
        if inside_c:
            result["marginal_c"] += mass
        if inside_b:
            result["marginal_b"] += mass
        if inside_c and inside_b:
            result["joint_rectangle"] += mass
        if lo_c + lo_b <= c + b <= hi_c + hi_b:
            result["sum_endpoints"] += mass
    return result


def build_report():
    """Run exact algebraic witnesses; these are not time-series experiments."""
    checks = {}
    scalar_p, scalar_c = Fraction(7, 3), Fraction(-5, 2)
    scalar_b = decompose_price(scalar_p, scalar_c)
    checks["decomposition"] = scalar_c + scalar_b == scalar_p
    checks["rw_identity"] = rw_plus_constant_basis(scalar_c, scalar_b) == scalar_p
    c = (Fraction(1, 3), Fraction(-2), Fraction(5, 7))
    b = (Fraction(3), Fraction(-2, 5), Fraction(4))
    p = tuple(ci + bi for ci, bi in zip(c, b))
    fixed = ((Fraction(2, 3), Fraction(-5, 7), Fraction(0)),)
    checks["fixed_operator"] = equivalence_gap(fixed, fixed, fixed, c, b) == (Fraction(0),)
    x = ((1, 0), (1, 1), (1, 2))
    ols = ols_operator(x)
    ridge = ridge_operator(x, Fraction(2), penalty=(0, 1))
    for name, operator in (("ols_same_design_fitted", ols), ("ridge_same_lambda_fitted", ridge)):
        fitted_c = apply_linear(x, apply_linear(operator, c))
        fitted_b = apply_linear(x, apply_linear(operator, b))
        fitted_p = apply_linear(x, apply_linear(operator, p))
        checks[name] = tuple(ci + bi for ci, bi in zip(fitted_c, fitted_b)) == fitted_p
    x_star = ((Fraction(1), Fraction(5, 2)),)
    forecast_c = apply_linear(x_star, apply_linear(ols, c))
    forecast_b = apply_linear(x_star, apply_linear(ols, b))
    forecast_p = apply_linear(x_star, apply_linear(ols, p))
    checks["common_xstar_forecast"] = tuple(ci + bi for ci, bi in zip(forecast_c, forecast_b)) == forecast_p
    first, second = ((1, 0, 0),), ((0, 1, 0),)
    checks["different_operator_counterexample"] = equivalence_gap(first, second, first, c, b) != (Fraction(0),)
    unit = ((1,),)
    checks["postprocess_counterexample"] = equivalence_gap(
        unit, unit, unit, (Fraction(-1),), (Fraction(2),),
        postprocess=lambda value: max(Fraction(0), value)) == (Fraction(1),)
    checks["covariance_effect"] = (combined_error_variance(4, 9, -6)
                                  < combined_error_variance(4, 9, 0)
                                  < combined_error_variance(4, 9, 6))
    atoms = ((Fraction(9, 10), 0, 0), (Fraction(1, 20), 2, 0), (Fraction(1, 20), 0, 2))
    coverage = finite_interval_coverages(atoms, (0, Fraction(1, 2)), (0, Fraction(1, 2)))
    checks["interval_counterexample"] = (coverage["marginal_c"] == coverage["marginal_b"] == Fraction(19, 20)
                                         and coverage["sum_endpoints"] == Fraction(9, 10))
    point_atoms = ((Fraction(2, 5), 0, 1), (Fraction(2, 5), 1, 0), (Fraction(1, 5), 0, 0))
    point_fixture = finite_point_functionals(point_atoms, Fraction(1, 2))
    checks["conditional_mean_additivity"] = (point_fixture["mean_c"] + point_fixture["mean_b"]
                                              == point_fixture["mean_p"])
    checks["median_nonadditivity"] = (point_fixture["quantile_c"] + point_fixture["quantile_b"]
                                      != point_fixture["quantile_p"])
    return {"scope": "pure_algebra_no_price_data_no_training", "all_passed": all(checks.values()),
            "not_evidence_of_predictive_gain": True, "checks": checks,
            "interval_counterexample": {key: str(value) for key, value in coverage.items()},
            "point_functional_fixture": {key: str(value) for key, value in point_fixture.items()},
            "limitations": ["Finite rational witnesses validate code; the general proof is in the design document.",
                            "Equivalence requires the same fixed operator, aligned inputs and common prediction row.",
                            "No fitted carbon prices, empirical coverage, model ranking or forecast skill is reported."]}


def main():
    """Emit a no-data algebra receipt to stdout; no files or inputs are read."""
    report = build_report()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["all_passed"] else 1


def _joint_atoms(atoms):
    """Validate an exact finite joint law; shared with interval checks."""
    atoms = tuple(tuple(_exact(value) for value in atom) for atom in atoms)
    if any(len(atom) != 3 for atom in atoms):
        raise ValueError("each atom must contain mass, C and B")
    if sum((atom[0] for atom in atoms), Fraction(0)) != 1:
        raise ValueError("joint probability masses must sum exactly to one")
    if any(atom[0] < 0 for atom in atoms):
        raise ValueError("probability masses must be nonnegative")
    return atoms


def finite_point_functionals(atoms, quantile=Fraction(1, 2)):
    """Means and lower quantiles of a specified law; no data are estimated.

    A fixed information set can be regarded as conditioning this finite law.
    Lower quantile convention: inf{x: Pr(Y<=x) >= q}.
    """
    atoms = _joint_atoms(atoms)
    quantile = _exact(quantile)
    if not 0 < quantile <= 1:
        raise ValueError("quantile level must be in (0, 1]")
    result = {}
    marginals = {"c": [(c, mass) for mass, c, b in atoms],
                 "b": [(b, mass) for mass, c, b in atoms],
                 "p": [(c + b, mass) for mass, c, b in atoms]}
    for name, pairs in marginals.items():
        result["mean_" + name] = sum((value * mass for value, mass in pairs), Fraction(0))
        cumulative = Fraction(0)
        for value, mass in sorted(pairs):
            cumulative += mass
            if cumulative >= quantile:
                result["quantile_" + name] = value
                break
        else:
            raise ValueError("quantile exceeds available unit mass")
    return result


if __name__ == "__main__":
    import sys
    sys.exit(main())
