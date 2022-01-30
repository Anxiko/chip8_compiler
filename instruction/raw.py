from binary_tools import byte_to_nibbles, raw_bytes_to_int


class RawInstruction:
	SIZE = 2
	_data: bytes

	def __init__(self, rom_bytes: bytes):
		if not isinstance(rom_bytes, bytes) or len(rom_bytes) != 2:
			raise TypeError(f"Invalid data for instruction: {rom_bytes}")
		self._data = rom_bytes

	def as_nibbles(self) -> tuple[int, int, int, int]:
		return byte_to_nibbles(self._data[0:1]) + byte_to_nibbles(self._data[1:2])

	def __repr__(self) -> str:
		padding_length: int = type(self).SIZE * 2 + 2
		return f"{type(self).__name__}<{raw_bytes_to_int(self._data):#0{padding_length}X}>"
