import requests

class Instruction:
    def __init__(self, prefix, opcode, instr_data):
        self.cbprefix = prefix == 'CBPrefixed'
        self.unprefix = prefix == 'Unprefixed'
        self.opcode = hex(opcode).upper()
        self.name = instr_data['Name']
        self.group = instr_data['Group']
        self.tcyclesbranch = instr_data['TCyclesBranch']
        self.tcyclesnobranch = instr_data['TCyclesNoBranch']
        self.length = instr_data['Length']
        self.flags = instr_data['Flags']
        self.timingnobranch = instr_data.get('TimingNoBranch', None)
        self.timingbranch = instr_data.get('TimingBranch', None)
        

r = requests.get("https://raw.githubusercontent.com/izik1/gbops/master/dmgops.json")
opcode_data = r.json()
opcodes = []
for prefix, instrs in opcode_data.items():
    for i, instr_data in enumerate(instrs):
        opcodes.append(Instruction(prefix, i, instr_data))
unpref = [o.name for o in opcodes if o.unprefix]
cbpref = [o.name for o in opcodes if o.cbprefix]
for i in unpref:
    print(i)


