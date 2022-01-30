from typing import BinaryIO, Iterator

from instruction import RawInstruction


def rom_file_instructions_iterator(rom_file: BinaryIO) -> Iterator[RawInstruction]:
	instruction_data: bytes
	while instruction_data := rom_file.read(RawInstruction.SIZE):
		match len(instruction_data):
			case 0:
				return
			case RawInstruction.SIZE:
				yield RawInstruction(instruction_data)
			case _:
				raise ValueError(f"Read incomplete instruction from ROM: {instruction_data}")
