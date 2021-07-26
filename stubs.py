import sys
import os
import shutil
import multiprocessing

import mypy.stubgen


if __name__ == '__main__':
    multiprocessing.freeze_support()
    stubgen_path = "."

    stubgen_path = "."
    if len(sys.argv) > 1:
        stubgen_path = sys.argv[1]

    sys.path.append(stubgen_path)

    opts = mypy.stubgen.parse_options([])
    opts.packages.append("pyfoil")
    opts.packages.append("xfoil")
    opts.output_dir = stubgen_path


    mypy.stubgen.generate_stubs(opts)

    xfoil_dir = os.path.join(stubgen_path, "xfoil-stubs")
    pyfoil_dir = os.path.join(stubgen_path, "pyfoil-stubs")

    for d in (xfoil_dir, pyfoil_dir):
        if os.path.isdir(d):
            shutil.rmtree(d)
            
    shutil.move(os.path.join(stubgen_path, "pyfoil"), pyfoil_dir)
    
    os.mkdir(xfoil_dir)
    shutil.move(os.path.join(stubgen_path, "xfoil.pyi"), os.path.join(xfoil_dir, "__init__.pyi"))