import glob
import os
import sys

from textx import TextXError
from metamodel import create_metamodel
from transformations import apply_transformations

if __name__ == '__main__':
    sources = sys.argv[1:] or sorted(glob.glob('models/*.arch'))
    mm = create_metamodel()
    failed = False
    for source in sources:
        try:
            model = mm.model_from_file(source)
        except TextXError as e:
            print(f'{source}: REJECTED: {e.message}')
            failed = True
            continue
        out = os.path.join('out', os.path.splitext(os.path.basename(source))[0])
        apply_transformations(model, out)
        print(f'{source}: conforms to the metamodel; artifacts written to {out}/')
    sys.exit(1 if failed else 0)
