from argparse import ArgumentParser
from tools.intcomp import ICC, load_program

def get_parser():
    parser = ArgumentParser('AoC Tools')

    parser.add_argument('--icc', help='Run the IntCode Computer.', action='store_true', default=True, dest='icc')
    parser.add_argument('-f', '--input', default='input', help='Input file.', dest='input_file')
    parser.add_argument('-I', '--interactive', default=False, action='store_true', dest='run_interactive')
    parser.add_argument('--verbose', dest='verbose', default=False, action='store_true', help='Run in verbose mode.')

    return parser

def run_icc(args):
    icc = ICC(load_program(args.input_file), [])
    if args.verbose:
        icc.verbose = True
    
    if args.run_interactive:
        icc.interactive = True
    icc.execute()

def run():
    parser = get_parser()

    args = parser.parse_args()

    if args.icc:
        run_icc(args)
    else:
        print('No command given.')
    

run()
