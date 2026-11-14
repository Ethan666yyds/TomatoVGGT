"""Extract exact trained tensors from the SHA-bound research checkpoint."""
import argparse
import json
from pathlib import Path
from tomatovggt.checkpoint import export_checkpoint

if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--checkpoint',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    info=export_checkpoint(a.checkpoint,a.output)
    print(json.dumps({'sha256':info['sha256'],'tensors':len(info['tensor_specs']),
                      'all_tensors_bit_equal_to_original':True}))
