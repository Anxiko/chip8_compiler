from abc import abstractmethod, ABC
from typing import Type

from binary_tools import nibbles_to_hex


class InstructionSymbol(ABC):
	nibbles: list[int]

	def __init__(self, nibbles: list[int]):
		self.nibbles = nibbles

	@classmethod
	def build(cls, nibbles: list[int]) -> 'InstructionSymbol':
		return cls(nibbles)

	@classmethod
	@abstractmethod
	def variable(cls) -> bool:
		pass

	@classmethod
	def builder(cls, length: int) -> 'SymbolBuilder':
		return SymbolBuilder(cls, length)

	def size(self) -> int:
		return len(self.nibbles)

	def __str__(self) -> str:
		return nibbles_to_hex(self.nibbles)

	def __repr__(self) -> str:
		return f"{type(self).__name__}<{str(self)}>"


class OpCodeSymbol(InstructionSymbol):
	@classmethod
	def variable(cls) -> bool:
		return False


class InstructionArgument(InstructionSymbol):
	@classmethod
	def variable(cls) -> bool:
		return True


class RegisterSymbol(InstructionArgument):
	register_number: int

	def __init__(self, nibbles: list[int]):
		super().__init__(nibbles)
		self.register_number = nibbles[0]

	def __str__(self) -> str:
		return f"V{self.register_number:01X}"

	@classmethod
	def fixed_builder(cls) -> 'SymbolBuilder':
		return cls.builder(1)


class ConstantSymbol(InstructionArgument):
	value: int

	def __init__(self, nibbles: list[int]):
		super().__init__(nibbles)
		self.value = type(self)._compute_value(self.nibbles)

	@staticmethod
	def _compute_value(nibbles: list[int]) -> int:
		rv: int = 0
		for index, nibble in enumerate(reversed(nibbles)):
			rv += nibble << (4 * index)

		return rv


class SymbolBuilder:
	symbol_type: Type[InstructionSymbol]
	symbol_length: int

	def __init__(self, symbol_type: Type[InstructionSymbol], symbol_length: int):
		self.symbol_type = symbol_type
		self.symbol_length = symbol_length

	def build_symbol(self, nibbles: list[int]) -> InstructionSymbol:
		return self.symbol_type.build(nibbles[:self.symbol_length])

	def variable(self) -> bool:
		return self.symbol_type.variable()

	def __repr__(self) -> str:
		return f"{type(self).__name__}({self.symbol_type}, {self.symbol_length})"
