from instruction import AsmInstructionBuilder, InstructionPattern, derive_instruction_builder_from_mask, RawInstruction, \
	AsmInstruction, UnknownAsmInstruction


class DispatcherMask:
	variable_mask: str


class DispatcherEntry:
	instruction_builder: AsmInstructionBuilder
	instruction_patterns: dict[tuple[int | None, ...], InstructionPattern]

	def __init__(self, variable_mask: str):
		self.instruction_builder = derive_instruction_builder_from_mask(variable_mask)
		self.instruction_patterns = {}

	def add_instruction_pattern(self, instruction_pattern: InstructionPattern):
		fixed_nibbles: tuple[int | None, ...] = tuple(instruction_pattern.get_fixed_nibbles())
		self.instruction_patterns[fixed_nibbles] = instruction_pattern

	def get_instruction(self, raw_instruction: RawInstruction) -> AsmInstruction | None:
		built_nibbles: tuple[int | None, ...] = tuple(self.instruction_builder.fixed_nibbles(raw_instruction))
		try:
			instruction_pattern: InstructionPattern | None = self.instruction_patterns[built_nibbles]
			return self.instruction_builder.build_instruction(raw_instruction, instruction_pattern.op_code)
		except KeyError:
			return None

	def __repr__(self) -> str:
		return f"{type(self).__name__}<{self.instruction_builder, self.instruction_patterns.values()}>"


class DecoderTranslator:
	_dispatcher_map: dict[str, DispatcherEntry]

	def __init__(self, instruction_patterns: list[InstructionPattern]):
		self._dispatcher_map = type(self)._compile_dispatcher_map(instruction_patterns)

	def get_instruction(self, raw_instruction) -> AsmInstruction:
		for mask, dispatcher_entry in self._dispatcher_map.items():
			asm_instruction: AsmInstruction | None = dispatcher_entry.get_instruction(raw_instruction)
			if asm_instruction is not None:
				return asm_instruction
		unknown_instruction: AsmInstruction = UnknownAsmInstruction(raw_instruction)
		print(f"Could not match instruction {raw_instruction}, mapping to {unknown_instruction}")
		return unknown_instruction

	@classmethod
	def _compile_dispatcher_map(
		cls, instruction_patterns: list[InstructionPattern]
	) -> dict[str, DispatcherEntry]:
		rv: dict[str, DispatcherEntry] = {}

		for instruction_pattern in instruction_patterns:
			variable_mask: str = instruction_pattern.get_variable_mask()
			dispatcher_entry: DispatcherEntry
			try:
				dispatcher_entry = rv[variable_mask]
			except KeyError:
				dispatcher_entry = DispatcherEntry(variable_mask)
				rv[variable_mask] = dispatcher_entry

			dispatcher_entry.add_instruction_pattern(instruction_pattern)

		return rv
