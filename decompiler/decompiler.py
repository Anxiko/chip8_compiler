from pathlib import Path

from instruction import AsmInstruction, INSTRUCTION_PATTERNS
from rom import rom_file_instructions_iterator
from .decoder import DecoderTranslator


def decompile(input_file: Path, output_file: Path) -> None:
	asm_instructions: list[AsmInstruction] = []
	dispatcher: DecoderTranslator = DecoderTranslator(INSTRUCTION_PATTERNS)
	with open(input_file, mode='rb') as rom_file:
		for raw_instruction in rom_file_instructions_iterator(rom_file):
			asm_instruction: AsmInstruction = dispatcher.get_instruction(raw_instruction)
			asm_instructions.append(asm_instruction)

	with open(output_file, mode='w', encoding='utf-8') as source_file:
		for asm_instruction in asm_instructions:
			instruction_text: str = str(asm_instruction)
			print(instruction_text, file=source_file)
