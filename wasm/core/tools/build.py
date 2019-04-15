#!/usr/bin/env python
from __future__ import print_function
import argparse
import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
WAST_DIR = os.path.join(ROOT_DIR, 'wast')
JS_DIR = os.path.join(ROOT_DIR, 'js')

HEADER = """\
// META: global=jsshell
// META: script=/wasm/core/harness.js
"""

def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('ref_interp',
        help="""Path to the WebAssembly reference interpreter.
        Build it by following the instructions here:
        https://github.com/WebAssembly/spec/tree/master/interpreter""")
    options = parser.parse_args(args)

    errors = []
    for wast_filename in sorted(os.listdir(WAST_DIR)):
        basename, ext = os.path.splitext(wast_filename)
        if ext != '.wast':
            continue

        wast_path = os.path.join(WAST_DIR, wast_filename)
        js_filename = basename + '.any.js'

        print('Processing {} -> {}'.format(wast_filename, js_filename))

        tmp_path = os.path.join(JS_DIR, basename + '.tmp.js')
        try:
            subprocess.check_call([options.ref_interp, '-h', '-d', wast_path,
                                   '-o', tmp_path])
        except subprocess.CalledProcessError as error:
            print('!! Failed to convert wast to js !!')
            errors.append(wast_filename)
            continue

        js_path = os.path.join(JS_DIR, js_filename)
        with open(tmp_path, 'r') as tmp_file:
            with open(js_path, 'w') as js_file:
                js_file.write(HEADER)
                js_file.write(tmp_file.read())

        os.remove(tmp_path)

    if errors:
        print('Finished with {} errors:'.format(len(errors)))
        for error in errors:
            print('  {}'.format(error))
    else:
        print('Done.')


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
