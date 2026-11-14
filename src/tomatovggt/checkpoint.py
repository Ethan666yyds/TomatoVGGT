"""Export and strictly restore the selected model without optimizer/RNG state."""
from __future__ import annotations
import json
from pathlib import Path
import torch
from safetensors.torch import load_file, save_file
from ._io import sha256_file

ORIGINAL_SHA256 = '9a437b710f3bd334b9ad1fe739ce1ec6ff3addb0977e04143d9f962820c69581'
BASE_SHA256 = 'f164acf60724910d8fe1578bb499d800850c7bb0948db7555c413f9fbe60467e'
BASE_REVISION = '860abec7937da0a4c03c41d3c269c366e82abdf9'
VENDOR_COMMIT = 'a288dd0f14786c93483e45524328726ab7b1b4ce'
SCHEMA = 'tomatovggt-inference-v1'
SOURCE_HASHES = {
    'models/lora.py': 'de1399062d20226cc9a561c3b134955774f97af86e1ea2004266e267177c44bc',
    'models/rgfu.py': 'd6d3b2d2a39d20f86e5320952df5a223b70001a372eb08203a2c2b3cbedaf2b6',
    'models/vggt.py': 'd139a4d6bbba646cffb30b83c127ecec0c0e1ce77420c83e921598f43f7be578',
}

def validate_model_sources():
    root = Path(__file__).parent
    for relative, expected in SOURCE_HASHES.items():
        if sha256_file(root/relative) != expected:
            raise ValueError(f'Original model source differs: {relative}')

def export_checkpoint(source: Path, output: Path) -> dict:
    """Only deserialize the hash-bound original research checkpoint."""
    if sha256_file(source) != ORIGINAL_SHA256:
        raise ValueError('The input is not the selected update-1000 checkpoint')
    validate_model_sources()
    state = torch.load(source, map_location='cpu', weights_only=False)
    engine = state['engine']
    if (engine['schema_version'] != 'tomatovggt-update-engine-v1'
            or engine['configuration']['checkpoint_trainable_only'] is not True
            or engine['counters']['update_steps'] != 1000):
        raise ValueError('Selected checkpoint schema/update mismatch')
    for relative, digest in SOURCE_HASHES.items():
        if state['input_binding'].get('src/tomatovggt/'+relative) != digest:
            raise ValueError('Checkpoint original source binding mismatch')
    tensors = engine['model']
    if not all(isinstance(v, torch.Tensor) and torch.isfinite(v).all() for v in tensors.values()):
        raise ValueError('Invalid model tensor')
    output.mkdir(parents=True, exist_ok=True)
    target = output/'tomatovggt.safetensors'
    if target.exists() or (output/'model.json').exists():
        raise FileExistsError('Export requires a fresh output directory')
    save_file({k:v.detach().cpu().contiguous() for k,v in tensors.items()}, str(target),
              metadata={'format':SCHEMA, 'original_checkpoint_sha256':ORIGINAL_SHA256, 'selected_update':'1000'})
    restored = load_file(str(target))
    if set(restored) != set(tensors) or any(not torch.equal(restored[k], tensors[k]) for k in tensors):
        raise ValueError('Export changed model tensors')
    metadata = {
        'schema':SCHEMA, 'model':'TomatoVGGT', 'checkpoint_file':target.name,
        'sha256':sha256_file(target), 'original_checkpoint_sha256':ORIGINAL_SHA256,
        'selected_update':1000, 'base_model':'facebook/VGGT-1B', 'base_revision':BASE_REVISION,
        'base_weights_sha256':BASE_SHA256, 'vggt_source_commit':VENDOR_COMMIT,
        'architecture':{'lora_rank':16, 'lora_alpha':32, 'skip_first_n_blocks':4, 'rgfu':True},
        'trainable_names':engine['configuration']['trainable_names'],
        'tensor_specs':{k:{'shape':list(v.shape),'dtype':str(v.dtype)} for k,v in tensors.items()},
        'model_source_sha256':SOURCE_HASHES, 'all_tensors_bit_equal_to_original':True,
        'standalone_full_model':False,
    }
    (output/'model.json').write_text(json.dumps(metadata,indent=2)+'\n')
    return metadata

def load_adapter(weights: Path, metadata: Path) -> tuple[dict, dict]:
    info = json.loads(metadata.read_text())
    fixed = {'schema':SCHEMA, 'original_checkpoint_sha256':ORIGINAL_SHA256, 'selected_update':1000,
             'base_revision':BASE_REVISION, 'base_weights_sha256':BASE_SHA256,
             'vggt_source_commit':VENDOR_COMMIT, 'model_source_sha256':SOURCE_HASHES,
             'architecture':{'lora_rank':16, 'lora_alpha':32, 'skip_first_n_blocks':4, 'rgfu':True}}
    if any(info.get(k) != v for k,v in fixed.items()):
        raise ValueError('Adapter metadata does not describe the selected model')
    if sha256_file(weights) != info['sha256']:
        raise ValueError('Adapter SHA256 mismatch')
    validate_model_sources()
    tensors = load_file(str(weights), device='cpu')
    specs = info['tensor_specs']
    if set(tensors) != set(specs):
        raise ValueError('Adapter tensor names differ from metadata')
    for name,value in tensors.items():
        if list(value.shape) != specs[name]['shape'] or str(value.dtype) != specs[name]['dtype'] or not torch.isfinite(value).all():
            raise ValueError(f'Invalid adapter tensor: {name}')
    return tensors, info

def restore_adapter(model, tensors: dict, info: dict):
    trained = {n:v for n,v in model.named_parameters() if v.requires_grad}
    if list(trained) != info['trainable_names']:
        raise ValueError('Model trainable parameter names/order differ')
    expected = dict(trained)
    expected.update(dict(model.named_buffers()))
    if set(expected) != set(tensors):
        raise ValueError('Model parameter/buffer names differ')
    for name,target in expected.items():
        source = tensors[name]
        if source.shape != target.shape or source.dtype != target.dtype or not torch.isfinite(source).all():
            raise ValueError(f'Model tensor shape/dtype/value mismatch: {name}')
    with torch.no_grad():
        for name,target in expected.items():
            target.copy_(tensors[name].to(target.device))
