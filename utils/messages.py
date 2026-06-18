def split_message(text: str, max_length: int = 4000) -> list[str]:
    if len(text) <= max_length:
        return [text]

    parts: list[str] = []
    remaining = text

    while len(remaining) > max_length:
        split_at = remaining.rfind("\n\n", 0, max_length + 1)
        if split_at <= 0:
            split_at = remaining.rfind("\n", 0, max_length + 1)
        if split_at <= 0:
            split_at = max_length

        part = remaining[:split_at].rstrip()
        if not part:
            part = remaining[:max_length]
            split_at = max_length

        parts.append(part)
        remaining = remaining[split_at:].lstrip("\n")

    if remaining:
        parts.append(remaining)

    return parts
