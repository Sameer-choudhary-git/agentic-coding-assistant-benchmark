def parse_user(record: str) -> dict:
    """Parse an id,name,email CSV-like record into a normalized user mapping."""
    parts = record.split(",")
    return {"id": parts[0], "name": parts[1], "email": parts[2]}
