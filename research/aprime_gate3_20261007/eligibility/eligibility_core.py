"""Calendar-index qualification, not forecasting or market-state certification."""
import datetime as dt
from fractions import Fraction


def _positive_integer(value):
    if type(value) is not int or value < 1:
        raise ValueError('Expected a positive integer')


def _boolean_flags(flags, length):
    if len(flags) != length or any(type(value) is not bool for value in flags):
        raise ValueError('Boolean flags must align with every calendar index')


def count_mature_pairs(pairs, forecast_index):
    """Count already-valid supervision whose label is available by this index."""
    if type(forecast_index) is not int or forecast_index < 0:
        raise ValueError('Invalid forecast index')
    seen = set()
    for pair in pairs:
        if not isinstance(pair, (tuple, list)) or len(pair) != 2:
            raise ValueError('Malformed supervision pair')
        start, end = pair
        if (type(start) is not int or type(end) is not int or start < 0
                or end <= start or start in seen):
            raise ValueError('Invalid or repeated supervision origin')
        seen.add(start)
    return sum(end <= forecast_index for start, end in pairs)


def supervision_pairs(feature_valid, label_valid, h):
    """Missing labels reject a pair; calendar endpoints are never moved."""
    _positive_integer(h)
    _boolean_flags(feature_valid, len(feature_valid))
    _boolean_flags(label_valid, len(feature_valid))
    return [(i, i + h) for i in range(len(feature_valid) - h)
            if feature_valid[i] and label_valid[i + h]]


def complete_history(present, lookback):
    """Require current and preceding lookback observations on the given axis."""
    if type(lookback) is not int or lookback < 0:
        raise ValueError('Lookback must be a nonnegative integer')
    _boolean_flags(present, len(present))
    return [i >= lookback and all(present[i - lookback:i + 1])
            for i in range(len(present))]


def leave_target_out(prices, weights, target):
    """Exact weighted quote, not an independent market or executable price."""
    parsed = {code: Fraction(value) for code, value in weights.items()}
    if any(value < 0 for value in parsed.values()) or sum(parsed.values()) != 1:
        raise ValueError('Compilation weights must be nonnegative and sum to one')
    others = {code: value for code, value in parsed.items()
              if code != target and value > 0}
    if not others or parsed.get(target, 0) <= 0:
        return None
    if any(prices.get(code) is None for code in others):
        return None
    return sum(weight * Fraction(prices[code]) for code, weight in others.items()) / sum(others.values())


def qualification_schedule(calendar, feature_valid, shared_label_valid,
                           target_label_valid, in_scope, *, h,
                           minimum_train, validation_count):
    """Prospective phase eligibility and separate retrospective scoring flags."""
    for number in (h, minimum_train, validation_count):
        _positive_integer(number)
    if not calendar or list(calendar) != sorted(set(calendar)):
        raise ValueError('Calendar must be sorted, unique and nonempty')
    for value in calendar:
        if not isinstance(value, str) or dt.date.fromisoformat(value).isoformat() != value:
            raise ValueError('Calendar must contain canonical ISO dates')
    for flags in (feature_valid, shared_label_valid, target_label_valid, in_scope):
        _boolean_flags(flags, len(calendar))
    pairs = supervision_pairs(feature_valid, shared_label_valid, h)
    counts = [count_mature_pairs(pairs, i) for i in range(len(calendar))]
    candidates = [i for i in range(len(calendar))
                  if in_scope[i] and feature_valid[i] and counts[i] >= minimum_train]
    validation = candidates[:validation_count]
    freeze = (validation[-1] + h if len(validation) == validation_count
              and validation[-1] + h < len(calendar) else None)
    ready = freeze is not None and all(
        in_scope[i + h] and target_label_valid[i + h] for i in validation)
    rows = []
    for i, date in enumerate(calendar):
        end = i + h
        if not in_scope[i]:
            score_reason = 'origin_outside_candidate_period'
        elif end >= len(calendar):
            score_reason = 'endpoint_outside_snapshot'
        elif not in_scope[end]:
            score_reason = 'endpoint_outside_candidate_period'
        elif not target_label_valid[end]:
            score_reason = 'target_endpoint_missing'
        else:
            score_reason = 'target_available'
        scorable = score_reason == 'target_available'
        if not in_scope[i]:
            phase = 'out_of_scope'
        elif not feature_valid[i]:
            phase = 'missing_past_features'
        elif counts[i] < minimum_train:
            phase = 'training_warmup'
        elif i in validation:
            phase = 'validation'
        elif freeze is None:
            phase = 'insufficient_validation_origins'
        elif i < freeze:
            phase = 'wait_validation_labels'
        elif not ready:
            phase = 'blocked_validation_targets'
        else:
            phase = 'evaluation'
        rows.append({'origin_index': i, 'origin_date': date,
                     'endpoint_index': end,
                     'endpoint_date': calendar[end] if end < len(calendar) else None,
                     'in_scope': in_scope[i], 'feature_valid': feature_valid[i],
                     'mature_training_pairs': counts[i], 'phase': phase,
                     'issue_eligible': phase in ('validation', 'evaluation'),
                     'target_scorable': bool(scorable), 'score_reason': score_reason})
    return {'rows': rows, 'validation_indices': validation,
            'parameter_freeze_index': freeze, 'validation_ready': bool(ready)}
