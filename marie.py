class marie:

	def __init__(self, input_file):

		if (input_file[len(input_file) - 4 : len(input_file)] != ".mas"): raise ValueError("input_file is not a .mas file")

		self.__input_file = open(input_file)

		if (self.__input_file == None): raise FileNotFoundError

		self.__raw_data = self.__input_file.read()

		self.__raw_instructions       : list[str]       = []
		self.__raw_operation_operands : list[list[str]] = []
		self.__parsed_instructions    : list[int]       = []
		self.__label_table            : dict[str, int]  = {}

		self.__instruction_opcode_table = {
			"jns"      : opcodes.JNS,
			"load"     : opcodes.LOAD,
			"store"    : opcodes.STORE,
			"add"      : opcodes.ADD,
			"subt"     : opcodes.SUBT,
			"input"    : opcodes.INPUT,
			"output"   : opcodes.OUTPUT,
			"halt"     : opcodes.HALT,
			"skipcond" : opcodes.SKIPCOND,
			"jump"     : opcodes.JUMP,
			"clear"    : opcodes.CLEAR,
			"addi"     : opcodes.ADDI,
			"jumpi"    : opcodes.JUMPI,
			"loadi"    : opcodes.LOADI,
			"storei"   : opcodes.STOREI
		}

		self.__opcode_function_table = {
			opcodes.JNS      : self.__jns__,
			opcodes.LOAD     : self.__load__,
			opcodes.STORE    : self.__store__,
			opcodes.ADD      : self.__add__,
			opcodes.SUBT     : self.__subt__,
			opcodes.INPUT    : self.__input__,
			opcodes.OUTPUT   : self.__output__,
			opcodes.HALT     : self.__halt__,
			opcodes.SKIPCOND : self.__skipcond__,
			opcodes.JUMP     : self.__jump__,
			opcodes.CLEAR    : self.__clear__,
			opcodes.ADDI     : self.__addi__,
			opcodes.JUMPI    : self.__jumpi__,
			opcodes.LOADI    : self.__loadi__,
			opcodes.STOREI   : self.__storei__
		}

		self.__literals_function_table = {
			literals.DEC : self.__dec__,
			literals.HEX : self.__hex__,
			literals.OCT : self.__oct__
		}

		self.__skipcond_literals_table = {
			"200": skipcond.LESSER_THAN,
			"400": skipcond.EQUALS,
			"800": skipcond.GREATER_THAN
		}

		self.__origin = 0
		self.__program_counter = 0
		self.__accumulator = 0

		self.__parse__()

	def __parse__(self):

		# split into lines
		self.__raw_instructions = self.__raw_data.split("\n")

		# remove comments
		for i in range(len(self.__raw_instructions)):

				if ("/" in self.__raw_instructions[i]):

					start_index = self.__raw_instructions[i].find("/")
					suffix = "".join([self.__raw_instructions[i][l] for l in range(start_index, len(self.__raw_instructions[i]))])
					self.__raw_instructions[i] = self.__raw_instructions[i].removesuffix(suffix)

		# remove empty lines
		temp_raw_instructions = self.__raw_instructions

		self.__raw_instructions = []

		for i in range(len(temp_raw_instructions)):

			if temp_raw_instructions[i] != "": self.__raw_instructions.append(temp_raw_instructions[i])

		del temp_raw_instructions

		# split into operation, operand
		for i in range(len(self.__raw_instructions)):

			self.__raw_operation_operands.append(self.__raw_instructions[i].split(" "))

		# find origin and then remove line
		if (self.__raw_operation_operands[0][0].lower() == "org"):

			self.__origin = int(self.__raw_operation_operands[0][1])

			self.__raw_operation_operands.pop(0)

		# convert all operations into opcodes
		for i in range(len(self.__raw_operation_operands)):

			if (self.__raw_operation_operands[i][0].lower() not in list(self.__instruction_opcode_table.keys())):

				self.__parsed_instructions.append(0)

				if (self.__raw_operation_operands[i][1].lower() in list(self.__literals_function_table.keys())):
					self.__parsed_instructions[len(self.__parsed_instructions) - 1] += self.__literals_function_table[self.__raw_operation_operands[i][1].lower()](self.__raw_operation_operands[i][2])
				else:
					self.__parsed_instructions[len(self.__parsed_instructions) - 1] += self.__instruction_opcode_table[self.__raw_operation_operands[i][1].lower()] << 12

				self.__label_table[self.__raw_operation_operands[i][0].lower().strip(",")] = i + self.__origin

				continue

			self.__parsed_instructions.append(self.__instruction_opcode_table[self.__raw_operation_operands[i][0].lower()] << 12)

			if (len(self.__raw_operation_operands[i]) < 2): continue

			if (self.__raw_operation_operands[i][1] in list(self.__skipcond_literals_table.keys())):

				self.__parsed_instructions[len(self.__parsed_instructions) - 1] += self.__skipcond_literals_table[self.__raw_operation_operands[i][1]]

		# add all of the parsed labels to opcodes
		for i in range(len(self.__raw_operation_operands)):

			if (self.__raw_operation_operands[i][0].lower() in list(self.__label_table.keys())): continue

			if (self.__raw_operation_operands[i][-1].lower() in list(self.__label_table.keys())):

				self.__parsed_instructions[i] += self.__label_table[self.__raw_operation_operands[i][-1].lower()]

	def __jns__(self, x):

		self.__parsed_instructions[x - self.__origin] = self.__program_counter + self.__origin

		self.__program_counter = x - self.__origin

	def __load__(self, x):

		self.__accumulator = self.__parsed_instructions[x - self.__origin]

	def __store__(self, x):

		self.__parsed_instructions[x - self.__origin] = self.__accumulator

	def __add__(self, x):

		self.__accumulator += self.__parsed_instructions[x - self.__origin]

	def __subt__(self, x):

		self.__accumulator -= self.__parsed_instructions[x - self.__origin]

	def __input__(self, x): self.__accumulator = int(input())

	def __output__(self, x): print(self.__accumulator)

	def __halt__(self, x): return 1

	def __skipcond__(self, x):

		if (
			self.__accumulator  < 0 and x == skipcond.LESSER_THAN  or
		  self.__accumulator == 0 and x == skipcond.EQUALS       or
			self.__accumulator  > 0 and x == skipcond.GREATER_THAN
			):
			self.__program_counter += 1

	def __jump__(self, x):

		self.__program_counter = x - self.__origin

		opcode = self.__parsed_instructions[self.__program_counter] >> 12
		operand = self.__parsed_instructions[self.__program_counter] - (opcode << 12)

		return self.__opcode_function_table[opcode](operand)

	def __clear__(self, x):

		self.__accumulator = 0

	def __addi__(self, x):

		self.__accumulator += self.__parsed_instructions[self.__parsed_instructions[x - self.__origin] - self.__origin]

	def __jumpi__(self, x):

		self.__program_counter = self.__parsed_instructions[x - self.__origin] - self.__origin

	def __loadi__(self, x):

		self.__accumulator = self.__parsed_instructions[self.__parsed_instructions[x - self.__origin] - self.__origin]

	def __storei__(self,  x):

		self.__parsed_instructions[self.__parsed_instructions[x - self.__origin] - self.__origin] = self.__accumulator

	def __dec__(self, x): return int(x)

	def __hex__(self, x):

		total = 0

		for i in x:
			if i in list("ABCDEF"):
				total += (list("ABCDEF").index(i) + 10) * pow(16, len(x) - list(x).index(i) - 1)
			else:
				total += int(i) * pow(16,  len(x) - list(x).index(i) - 1)

		return total

	def __oct__(self, x):

		total = 0

		for i in x:
			total += int(i) * pow(8,  len(x) - list(x).index(i) - 1)

		return total

	def execute(self):

		while (True):

			opcode = self.__parsed_instructions[self.__program_counter] >> 12
			operand = self.__parsed_instructions[self.__program_counter] - (opcode << 12)

			if (self.__opcode_function_table[opcode](operand) == 1): break

			self.__program_counter += 1

class opcodes:

	JNS      = 0x0
	LOAD     = 0x1
	STORE    = 0x2
	ADD      = 0x3
	SUBT     = 0x4
	INPUT    = 0x5
	OUTPUT   = 0x6
	HALT     = 0x7
	SKIPCOND = 0x8
	JUMP     = 0x9
	CLEAR    = 0xA
	ADDI     = 0xB
	JUMPI    = 0xC
	LOADI    = 0xD
	STOREI   = 0xE

class literals:

	DEC = "dec"
	HEX = "hex"
	OCT = "oct"

class skipcond:

	LESSER_THAN  = 0x000
	EQUALS       = 0x400
	GREATER_THAN = 0x800