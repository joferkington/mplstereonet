"""
Automatically generate rst files for examples.

Avoiding matplotlib sphinx plot directive, as we want a bit more control over
how things are displayed and how output text is displayed.
"""
import sys
import os

DOCDIR = os.path.dirname(__file__)
sys.path.append(os.path.join(DOCDIR, '..', 'tests'))

import examples

def main():
    example_index()
    for filename in examples.example_files():
        filename = os.path.relpath(filename)
        text, figures = examples.run(filename)
        generate_rst(filename, text, figures)

def save_figures(figures, example_filename):
    _, base = os.path.split(example_filename)
    base, _ = os.path.splitext(base)
    out = os.path.join(DOCDIR, '_static', 'examples', base)

    files = []
    for i, fig in enumerate(figures):
        name = '{}_{}.png'.format(out, i)
        fig.savefig(name, dpi=80)
        files.append(name)

    return files

def example_index():
    dirname = os.path.join(DOCDIR, 'examples')
    static = os.path.join(DOCDIR, '_static', 'examples')
    os.makedirs(dirname, exist_ok=True)
    os.makedirs(static, exist_ok=True)

    path = os.path.join(DOCDIR, 'examples', 'index.rst')
    with open(path, 'w') as outfile:
        outfile.write('Examples\n')
        outfile.write('========\n\n')
        outfile.write('.. toctree::\n')
        outfile.write('   :maxdepth: 1\n\n')
        for filename in sorted(list(examples.example_files())):
            _, basename = os.path.split(filename)
            base, _ = os.path.splitext(basename)
            outfile.write('   {}\n'.format(base))

def generate_rst(example_filename, output_text, figures):
    descrip_text, code = split_description(example_filename)

    _, basename = os.path.split(example_filename)
    base, _ = os.path.splitext(basename)

    outname = os.path.join(DOCDIR, 'examples', base + '.rst')

    with open(outname, 'w') as outfile:
        outfile.write('``{}``\n'.format(basename))
        outfile.write('=' * (len(basename) + 4) + '\n\n')

        if descrip_text:
            outfile.write(descrip_text + '\n\n')

        outfile.write('.. code-block:: python\n')
        for line in code.split('\n'):
            outfile.write('    {}\n'.format(line))

        outfile.write('\nResult\n------\n\n')
        if figures:
            for name in save_figures(figures, example_filename):
                outfile.write('.. image:: /{}\n'.format(name))
                outfile.write('    :align: center\n\n')

        if output_text:
            outfile.write('.. code-block:: text\n\n')
            for line in output_text.split('\n'):
                outfile.write('    ' + line + '\n')
            outfile.write('\n')

        outfile.write('\n')


def split_description(filename):
    with open(filename, 'r') as infile:
        code = infile.read().split('"""', 2)
        if len(code) == 1:
            return '', code[0]
        else:
            return code[1], code[2]

if __name__ == '__main__':
    main()
