"""Field validators shared by the typed boundary objects. Each raises ValueError naming the field."""
import math

import numpy as np


def name(value, field, maximum=160):
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise ValueError(f'{field} must be a nonempty string of at most {maximum} characters')
    return value


def time(value, field):
    try:
        value = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f'{field} must be finite and nonnegative') from error
    if not math.isfinite(value) or not 0 <= value <= 1e12:
        raise ValueError(f'{field} must be finite and nonnegative')
    return value


def ids(values, field, maximum=512):
    if not isinstance(values, (list, tuple)) or len(values) > maximum:
        raise ValueError(f'{field} must be a bounded list of IDs')
    return list(dict.fromkeys(name(value, field) for value in values))


def unit(values):
    vector = np.asarray(values, dtype=np.float64)
    if vector.ndim != 1 or not 2 <= len(vector) <= 4096 or not np.isfinite(vector).all():
        raise ValueError('features must be a finite one-dimensional vector of 2-4096 values')
    norm = float(np.linalg.norm(vector))
    if not math.isfinite(norm) or norm < 1e-10:
        raise ValueError('zero or numerically unbounded features cannot form a motif')
    return vector / norm
