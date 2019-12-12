from argparse import ArgumentParser
from tools.intcomp import ICC, load_program, Disassembler

def get_parser():
    parser = ArgumentParser('AoC Tools')

    parser.add_argument('--icc', help='Run the IntCode Computer.', action='store_true', default=True, dest='icc')
    parser.add_argument('-D', '--disasm', action='store_true', default=False, dest='disasm', help='Disassemble the program.')
    parser.add_argument('-f', '--input', default='input', help='Input file.', dest='input_file')
    parser.add_argument('-I', '--interactive', default=False, action='store_true', dest='run_interactive')
    parser.add_argument('--verbose', dest='verbose', default=False, action='store_true', help='Run in verbose mode.')
    parser.add_argument('--show-comments', dest='show_comments', default=True, action='store_true', help='Show comments for disassembled program.')

    return parser

def run_icc(args):

    def read():
        val = input('(Input required) READ>')
        return int(val.strip() or '0')

    icc = ICC(load_program(args.input_file), inpq=read)
    if args.verbose:
        icc.verbose = True
    
    if args.run_interactive:
        icc.interactive = True
    icc.execute()


def disassemble(args):
    disasm = Disassembler(load_program(args.input_file), show_comments=args.show_comments)

    for line in disasm.dump_mem():
        print(line)


def run():
    parser = get_parser()

    args = parser.parse_args()

    if args.disasm:
        disassemble(args)
    elif args.icc:
        run_icc(args)
    else:
        print('No command given.')
    

run()
