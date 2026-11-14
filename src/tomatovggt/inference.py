"""RGB -> depth and colored point cloud using calibrated rig cameras."""
from __future__ import annotations
import argparse
from contextlib import nullcontext
import json
import math
from pathlib import Path
import time
import numpy as np
import torch
from PIL import Image
from ._io import sha256_file
from .checkpoint import load_adapter, restore_adapter, BASE_SHA256, VENDOR_COMMIT
from .data.preprocessing import preprocess_image, preprocess_spec
from .models.vggt import load_vggt

def load_inputs(images_dir: Path, cameras: Path, expected_views: int = 15):
    spec = json.loads(cameras.read_text())
    ids = spec['view_ids']
    if (len(ids) != expected_views or len(set(ids)) != len(ids)
            or any(not isinstance(v,str) or not v or '/' in v or '\\' in v or v in ('.','..') for v in ids)):
        raise ValueError('Camera view_ids must be ordered, unique and match --expected-views')
    rows = spec['views']
    if [str(row['camera_id']) for row in rows] != ids:
        raise ValueError('Camera rows must match the explicit view order')
    frames=[];intrinsics=[];extrinsics=[];files=[]
    for view,row in zip(ids,rows):
        matches=[p for p in images_dir.iterdir() if p.is_file() and p.stem==view and p.suffix.lower() in ('.png','.jpg','.jpeg')]
        if len(matches)!=1:
            raise ValueError(f'Expected exactly one RGB image for view {view}')
        path=matches[0]
        with Image.open(path) as image:
            if 'width' in row and image.size!=(row['width'],row['height']):
                raise ValueError(f'Calibration/image dimensions differ for view {view}')
        frame=preprocess_image(path)
        if 'K_raw' not in row and 'K' not in row:
            raise ValueError('Each camera needs raw-image K or K_raw')
        kraw=np.asarray(row.get('K_raw',row.get('K')),dtype=np.float64)
        if (kraw.shape!=(3,3) or not np.isfinite(kraw).all() or kraw[0,0]<=0 or kraw[1,1]<=0
                or not np.allclose(kraw[2],[0,0,1],rtol=0,atol=1e-7)):
            raise ValueError('Invalid camera intrinsics')
        k=frame['pixel_transform'].numpy().astype(np.float64)@kraw
        if 'K_518' in row and not np.allclose(k,row['K_518'],rtol=0,atol=1e-4):
            raise ValueError('Frozen K_518 differs from actual image preprocessing')
        t=np.asarray(row['T_world_to_camera'],dtype=np.float64)
        if t.shape==(4,4):
            if not np.allclose(t[3],[0,0,0,1],rtol=0,atol=1e-7):raise ValueError('Invalid homogeneous camera transform')
            t=t[:3]
        if (t.shape!=(3,4) or not np.isfinite(t).all()
                or not np.allclose(t[:,:3]@t[:,:3].T,np.eye(3),rtol=0,atol=1e-5)
                or not np.isclose(np.linalg.det(t[:,:3]),1,rtol=0,atol=1e-5)):
            raise ValueError('Invalid world-to-camera transform')
        frames.append(frame);intrinsics.append(k);extrinsics.append(t);files.append(path)
    return {'images':torch.stack([f['images'] for f in frames]),
            'spatial_valid':np.stack([f['spatial_valid'].numpy() for f in frames]),
            'intrinsics':np.asarray(intrinsics,dtype=np.float32),
            'extrinsics':np.asarray(extrinsics,dtype=np.float32),'view_ids':ids,'files':files}

def unproject(depth, rgb, valid, intrinsic, extrinsic, stride=1):
    if type(stride) is not int or stride<1:raise ValueError('point stride must be positive')
    if (depth.ndim!=3 or rgb.shape!=(*depth.shape,3) or valid.shape!=depth.shape
            or intrinsic.shape!=(len(depth),3,3) or extrinsic.shape!=(len(depth),3,4)):
        raise ValueError('Point cloud array shapes differ')
    points=[];colors=[]
    sampled=np.zeros(depth.shape[-2:],dtype=bool);sampled[::stride,::stride]=True
    for z,image,mask,k,t in zip(depth,rgb,valid,intrinsic,extrinsic):
        v,u=np.nonzero(mask & sampled & np.isfinite(z) & (z>0))
        pixels=np.stack((u+.5,v+.5,np.ones(len(u))),axis=-1)
        xyz=(pixels@np.linalg.inv(k).T)*z[v,u,None]
        world=(xyz-t[:,3])@t[:,:3]
        points.append(world.astype(np.float32));colors.append(image[v,u])
    return np.concatenate(points),np.concatenate(colors)

def write_ply(path, points, colors):
    if points.shape!=(len(colors),3) or colors.shape!=(len(points),3):raise ValueError('Invalid PLY arrays')
    vertices=np.empty(len(points),dtype=[('x','<f4'),('y','<f4'),('z','<f4'),('red','u1'),('green','u1'),('blue','u1')])
    for j,name in enumerate(('x','y','z')):vertices[name]=points[:,j]
    for j,name in enumerate(('red','green','blue')):vertices[name]=colors[:,j]
    header=('ply\nformat binary_little_endian 1.0\n'+f'element vertex {len(points)}\n'+
            'property float x\nproperty float y\nproperty float z\nproperty uchar red\nproperty uchar green\nproperty uchar blue\nend_header\n')
    with path.open('wb') as f:f.write(header.encode());f.write(vertices.tobytes())

def run(args):
    if args.output.exists():raise FileExistsError('Choose a new output directory')
    if not math.isfinite(args.depth_scale) or args.depth_scale<=0:raise ValueError('Depth scale must be positive and finite')
    if args.point_stride<1:raise ValueError('Point stride must be positive')
    if args.threads<1:raise ValueError('CPU threads must be positive')
    torch.set_num_threads(args.threads)
    batch=load_inputs(args.images_dir,args.cameras,args.expected_views)
    tensors,info=load_adapter(args.weights,args.model_metadata or args.weights.with_name('model.json'))
    device=torch.device(args.device)
    if device.type=='cuda' and not torch.cuda.is_available():raise RuntimeError('CUDA is unavailable; choose --device cpu')
    if device.type=='cuda' and not torch.cuda.is_bf16_supported():raise RuntimeError('Published CUDA inference requires BF16 support')
    print(json.dumps({'stage':'loading_model','views':len(batch['view_ids']),'device':str(device)}),flush=True)
    model=load_vggt(args.vggt_source,args.base_weights,BASE_SHA256,VENDOR_COMMIT,device='cpu',rank=16,alpha=32,rgfu=True)
    restore_adapter(model,tensors,info)
    del tensors
    model.eval().to(device)
    images=batch['images'].to(device)
    if device.type=='cuda':torch.cuda.synchronize()
    start=time.perf_counter()
    precision=torch.autocast('cuda',dtype=torch.bfloat16) if device.type=='cuda' else nullcontext()
    print(json.dumps({'stage':'forward','precision':'BF16 aggregator / FP32 head' if device.type=='cuda' else 'FP32'}),flush=True)
    with torch.inference_mode(),precision:prediction=model(images,include_camera=False)
    if device.type=='cuda':torch.cuda.synchronize()
    elapsed=time.perf_counter()-start
    depth=prediction['depth'].float().cpu().numpy()*args.depth_scale
    conf=prediction['depth_conf'].float().cpu().numpy()
    if depth.shape!=(len(batch['view_ids']),518,518) or not np.isfinite(depth).all() or not np.isfinite(conf).all():
        raise ValueError('Network produced invalid depth/confidence')
    rgb=np.clip(np.rint(batch['images'].permute(0,2,3,1).numpy()*255),0,255).astype(np.uint8)
    points,colors=unproject(depth,rgb,batch['spatial_valid'],batch['intrinsics'],batch['extrinsics'],args.point_stride)
    if not len(points):raise ValueError('No finite positive depth points')
    args.output.mkdir(parents=True)
    np.savez_compressed(args.output/'prediction.npz',depth=depth,depth_conf=conf,intrinsics=batch['intrinsics'],
                        extrinsics=batch['extrinsics'],spatial_valid=batch['spatial_valid'],view_ids=np.asarray(batch['view_ids']))
    write_ply(args.output/'point_cloud.ply',points,colors)
    provenance={'model':'TomatoVGGT','selected_update':1000,'weights_sha256':info['sha256'],
                'base_weights_sha256':BASE_SHA256,'vggt_source_commit':VENDOR_COMMIT,
                'camera_source':'provided calibrated rig; world_to_camera; metres',
                'cameras_sha256':sha256_file(args.cameras),'view_ids':batch['view_ids'],
                'image_sha256':{v:sha256_file(p) for v,p in zip(batch['view_ids'],batch['files'])},
                'preprocessing':preprocess_spec(),'depth_scale':args.depth_scale,
                'reference_geometry_used':False,'alignment_performed':False,
                'point_stride':args.point_stride,'points':len(points),'device':str(device),
                'precision':'bf16_aggregator_fp32_head' if device.type=='cuda' else 'float32',
                'forward_seconds_unwarmed':elapsed,'torch':torch.__version__}
    (args.output/'inference.json').write_text(json.dumps(provenance,indent=2)+'\n')
    print(json.dumps({'stage':'complete','points':len(points),'forward_seconds':elapsed,'output':str(args.output)}),flush=True)
    return provenance

def parser():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--images-dir',type=Path,required=True)
    p.add_argument('--cameras',type=Path,required=True)
    p.add_argument('--weights',type=Path,default=Path('weights/tomatovggt.safetensors'))
    p.add_argument('--model-metadata',type=Path)
    p.add_argument('--base-weights',type=Path,required=True)
    p.add_argument('--vggt-source',type=Path,default=Path('vendor/vggt'))
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--device',choices=['cuda','cpu'],default='cuda')
    p.add_argument('--expected-views',type=int,default=15)
    p.add_argument('--depth-scale',type=float,default=1.)
    p.add_argument('--point-stride',type=int,default=1)
    p.add_argument('--threads',type=int,default=8)
    return p

def main():run(parser().parse_args())

if __name__=='__main__':main()
