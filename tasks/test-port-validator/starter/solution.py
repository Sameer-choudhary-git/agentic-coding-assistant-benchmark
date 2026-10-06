def is_valid_port(value) -> bool:
    """Return whether value is an integer TCP/UDP port in the valid range."""
    return isinstance(value, int) and not isinstance(value, bool) and 1 <= value <= 65535
