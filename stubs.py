import sys
import os
import shutil
import multiprocessing

import mypy.stubgen


if __name__ == '__main__':
    multiprocessing.freeze_support()
    stubgen_path = "./stubs"

    sys.path.append(stubgen_path)

    opts = mypy.stubgen.parse_options([])
    opts.packages.append("pyfoil")
    opts.packages.append("xfoil")
    opts.output_dir = stubgen_path


    mypy.stubgen.generate_stubs(opts)

    for d in ("pyfoil-stubs", "xfoil-stubs"):
        if os.path.isdir(d):
            shutil.rmtree(d)
            
    shutil.move(os.path.join(stubgen_path, "pyfoil"), "pyfoil-stubs")
    
    os.mkdir("xfoil-stubs")
    shutil.move(os.path.join(stubgen_path, "xfoil.pyi"), "xfoil-stubs/__init__.pyi")

    shutil.rmtree("stubs")