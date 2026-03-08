import math

def decay_score(importance, age_days, decay_factor=30):
    """Returns the decayed importance score."""
    return importance * math.exp(-age_days / decay_factor)