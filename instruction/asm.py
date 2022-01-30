from itertools import chain
from typing import Iterable

from .raw import RawInstruction
from .symbols import InstructionSymbol, SymbolBuilder, OpCodeSymbol


class AsmInstruction:
	raw_instruction: RawInstruction
	op_code: str
	symbols: list[InstructionSymbol]

	def __init__(
		self, raw_instruction: RawInstruction, op_code: str, symbols: list[InstructionSymbol]
	):
		self.raw_instruction = raw_instruction
		self.op_code = op_code
		self.symbols = symbols

	@staticmethod
	def _symbol_is_variable(symbol: InstructionSymbol) -> bool:
		return symbol.variable()

	def _get_variable_symbols(self) -> Iterable[InstructionSymbol]:
		return filter(type(self)._symbol_is_variable, self.symbols)

	def __repr__(self):
		return " ".join(chain([self.op_code], map(str, self._get_variable_symbols())))


class UnknownAsmInstruction(AsmInstruction):
	entire_op_code_symbol: OpCodeSymbol

	def __init__(self, raw_instruction: RawInstruction):
		self.entire_op_code_symbol = OpCodeSymbol(list(raw_instruction.as_nibbles()))
		super().__init__(raw_instruction, "UNKNOWN", [self.entire_op_code_symbol])

	def __repr__(self) -> str:
		return f"{self.op_code} {str(self.entire_op_code_symbol)}"


class AsmInstructionBuilder:
	symbol_builders: list[SymbolBuilder]

	def __init__(self, symbol_builders: list[SymbolBuilder]):
		self.symbol_builders = symbol_builders

	def fixed_nibbles(self, raw_instruction: RawInstruction) -> list[int | None]:
		rv: list[int | None] = []
		nibbles: list[int] = list(raw_instruction.as_nibbles())

		for symbol_builder in self.symbol_builders:
			if symbol_builder.variable():
				rv.extend([None] * symbol_builder.symbol_length)
				nibbles = nibbles[symbol_builder.symbol_length:]
			else:
				rv.extend(nibbles[:symbol_builder.symbol_length])
				nibbles = nibbles[symbol_builder.symbol_length:]

		return rv

	def build_instruction(self, raw_instruction: RawInstruction, op_code: str) -> AsmInstruction:
		instruction_nibbles: list[int] = list(raw_instruction.as_nibbles())
		remaining_nibbles: list[int] = instruction_nibbles

		symbols: list[InstructionSymbol] = []
		for symbol_builder in self.symbol_builders:
			symbol_nibbles: list[int] = remaining_nibbles[:symbol_builder.symbol_length]
			remaining_nibbles = remaining_nibbles[symbol_builder.symbol_length:]
			symbol: InstructionSymbol = symbol_builder.build_symbol(symbol_nibbles)
			symbols.append(symbol)

		return AsmInstruction(raw_instruction, op_code, symbols)

	def __repr__(self) -> str:
		return f"{type(self).__name__}({self.symbol_builders})"
