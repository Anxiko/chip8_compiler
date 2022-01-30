def byte_to_nibbles(byte: bytes) -> tuple[int, int]:
	as_int: int = byte[0]
	return as_int >> 4, 0xF & as_int


def nibbles_to_int(nibbles: list[int]) -> int:
	rv: int = 0
	for idx, nibble in enumerate(reversed(nibbles)):
		rv += nibble << 4 * idx

	return rv


def nibbles_to_hex(nibbles: list[int], with_prefix: bool = True, uppercase: bool = True) -> str:
	value: int = nibbles_to_int(nibbles)
	min_length = len(nibbles) + (2 if with_prefix else 0)
	hex_format_character: str = 'X' if uppercase else 'x'
	prefix_format_character: str = '#' if with_prefix else ''

	return f"{value:{prefix_format_character}0{min_length}{hex_format_character}}"


def raw_bytes_to_int(instruction_bytes: bytes) -> int:
	return int.from_bytes(instruction_bytes, 'big', signed=False)
