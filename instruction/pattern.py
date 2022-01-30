import re
from typing import Type, Iterator

from .asm import AsmInstructionBuilder
from .symbols import InstructionSymbol, RegisterSymbol, ConstantSymbol, SymbolBuilder, OpCodeSymbol

_INSTRUCTION_SYMBOL_CHARACTER_MAPPING: dict[str, Type[InstructionSymbol]] = {
	'N': ConstantSymbol,
	'X': RegisterSymbol,
	'Y': RegisterSymbol,
}

_INSTRUCTION_SYMBOL_CHARACTERS: str = ''.join(_INSTRUCTION_SYMBOL_CHARACTER_MAPPING.keys())


class InstructionPattern:
	_MASK_CHARACTER: str = '_'
	_PATTERN: re.Pattern = re.compile(fr'[0-9A-F{_INSTRUCTION_SYMBOL_CHARACTERS}]{{4}}')

	op_code: str
	hex_pattern: str
	_fixed_nibbles: list[int | None]
	_hex_fixed_mask: str
	_hex_variable_mask: str

	def __init__(self, hex_pattern: str, op_code: str):
		type(self)._validate_hex_pattern(hex_pattern)
		self.hex_pattern = hex_pattern
		self.op_code = op_code
		self._hex_fixed_mask, self._hex_variable_mask = type(self)._divide_pattern_into_masks(hex_pattern)
		self._fixed_nibbles = type(self)._build_matchable_nibbles(self._hex_fixed_mask)

	def get_fixed_nibbles(self) -> list[int | None]:
		return self._fixed_nibbles

	def get_fixed_mask(self) -> str:
		return self._hex_fixed_mask

	def get_variable_mask(self) -> str:
		return self._hex_variable_mask

	@classmethod
	def _validate_hex_pattern(cls, hex_pattern: str) -> None:
		pattern_match: re.Match | None = cls._PATTERN.match(hex_pattern)
		if pattern_match is None:
			raise ValueError(f"Invalid hex pattern: {hex_pattern}")

	@classmethod
	def _divide_pattern_into_masks(cls, hex_pattern: str) -> tuple[str, str]:
		fixed_mask: str = ''
		variable_mask: str = ''

		for character in hex_pattern:
			if character in _INSTRUCTION_SYMBOL_CHARACTERS:
				variable_mask += character
				fixed_mask += '_'
			else:
				variable_mask += '_'
				fixed_mask += character

		return fixed_mask, variable_mask

	@classmethod
	def _build_matchable_nibbles(cls, hex_pattern) -> list[int | None]:
		rv: list[int | None] = []
		for hex_digit in hex_pattern:
			digit_value: int | None
			if hex_digit == '_':
				digit_value = None
			else:
				digit_value = int(hex_digit, 16)
			rv.append(digit_value)
		return rv


INSTRUCTION_PATTERNS: list[InstructionPattern] = [
	# InstructionPattern('0NNN', 'INVOKE'),
	InstructionPattern('00E0', 'CLEAR'),
	InstructionPattern('00EE', 'RETURN'),
	InstructionPattern('1NNN', 'GOTO'),
	InstructionPattern('2NNN', 'CALL'),
	InstructionPattern('3XNN', 'SIEQ'),
	InstructionPattern('4XNN', 'SINE'),
	InstructionPattern('5XY0', 'SREQ'),
	InstructionPattern('6XNN', 'SETR'),
	InstructionPattern('7XNN', 'ADDI'),
	InstructionPattern('8XY0', 'COPY'),
	InstructionPattern('8XY1', 'OR'),
	InstructionPattern('8XY2', 'AND'),
	InstructionPattern('8XY3', 'XOR'),
	InstructionPattern('8XY4', 'ADD'),
	InstructionPattern('8XY5', 'SUB'),
	InstructionPattern('8XY6', 'SHIFTR'),
	InstructionPattern('8XY7', 'SUB-'),
	InstructionPattern('8XYE', 'SHIFTL'),
	InstructionPattern('9XY0', 'SRNE'),
	InstructionPattern('ANNN', 'SETI'),
	InstructionPattern('BNNN', 'JUMPR'),
	InstructionPattern('CXNN', 'RAND'),
	InstructionPattern('DXYN', 'DRAW'),
	InstructionPattern('EX9E', 'SKPR'),
	InstructionPattern('EXA1', 'SKNP'),
	InstructionPattern('FX07', 'RDEL'),
	InstructionPattern('FX0A', 'KEY'),
	InstructionPattern('FX15', 'TDEL'),
	InstructionPattern('FX18', 'TSND'),
	InstructionPattern('FX1E', 'IADD'),
	InstructionPattern('FX29', 'CHAR'),
	InstructionPattern('FX33', 'DEC'),
	InstructionPattern('FX55', 'DUMP'),
	InstructionPattern('FX65', 'LOAD'),
]


def _mask_part_to_symbol_builder(mask_part: str) -> SymbolBuilder:
	symbol_type: Type[InstructionSymbol] = _INSTRUCTION_SYMBOL_CHARACTER_MAPPING.get(
		mask_part[0],
		OpCodeSymbol
	)
	return SymbolBuilder(symbol_type, len(mask_part))


def _mask_parts_generator(mask: str) -> Iterator[str]:
	current_mask_part: str = ''
	for character in mask:
		if len(current_mask_part) == 0 or current_mask_part[-1] == character:
			current_mask_part += character
		else:
			yield current_mask_part
			current_mask_part = character
	if len(current_mask_part) > 0:
		yield current_mask_part
	return


def derive_instruction_builder_from_mask(mask: str) -> AsmInstructionBuilder:
	return AsmInstructionBuilder(
		list(map(_mask_part_to_symbol_builder, _mask_parts_generator(mask)))
	)
