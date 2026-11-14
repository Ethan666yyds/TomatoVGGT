import json
from pathlib import Path
import tempfile
import unittest
import numpy as np
from PIL import Image
import torch
from torch import nn
from tomatovggt.inference import load_inputs, unproject, write_ply
from tomatovggt.checkpoint import restore_adapter, validate_model_sources

class InferenceBehaviorTests(unittest.TestCase):
    def test_explicit_view_order_preprocessing_and_intrinsic_mapping(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);ids=['2','0','1'];rows=[]
            k=np.array([[4.,0.,1.],[0.,4.,2.],[0.,0.,1.]])
            for i in ids:
                Image.new('RGB',(2,4),(int(i)*30,0,0)).save(root/f'{i}.png')
                rows.append({'camera_id':i,'width':2,'height':4,'K':k.tolist(),'T_world_to_camera':np.eye(4).tolist()})
            cameras=root/'cameras.json';cameras.write_text(json.dumps({'view_ids':ids,'views':rows}))
            batch=load_inputs(root,cameras,3)
            self.assertEqual(batch['view_ids'],ids)
            self.assertEqual(list(batch['images'].shape),[3,3,518,518])
            np.testing.assert_allclose(batch['intrinsics'][0],np.array([[518,0,259],[0,518,259],[0,0,1]]))
            self.assertEqual(int(batch['spatial_valid'][0].sum()),259*518)
            self.assertGreater(float(batch['images'][0,0].sum()),float(batch['images'][2,0].sum()))
            (root/'1.png').rename(root/'missing.png')
            with self.assertRaisesRegex(ValueError,'view 1'):load_inputs(root,cameras,3)

    def test_half_pixel_world_to_camera_unprojection_and_mask(self):
        depth=np.array([[[2.,np.nan],[0.,3.]]],dtype=np.float32)
        rgb=np.arange(12,dtype=np.uint8).reshape(1,2,2,3)
        valid=np.array([[[True,True],[True,False]]])
        k=np.array([[[1,0,.5],[0,1,.5],[0,0,1]]],dtype=np.float32)
        t=np.eye(4,dtype=np.float32)[None,:3];t[0,0,3]=1
        points,colors=unproject(depth,rgb,valid,k,t)
        np.testing.assert_array_equal(points,[[-1,0,2]])
        np.testing.assert_array_equal(colors,[[0,1,2]])

    def test_ply_binary_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'cloud.ply'
            points=np.array([[1,2,3],[-1,.5,0]],dtype=np.float32)
            colors=np.array([[255,0,100],[10,20,30]],dtype=np.uint8)
            write_ply(path,points,colors)
            header,body=path.read_bytes().split(b'end_header\n',1)
            self.assertIn(b'element vertex 2',header)
            dtype=np.dtype([('xyz','<f4',3),('rgb','u1',3)])
            rows=np.frombuffer(body,dtype=dtype)
            np.testing.assert_array_equal(rows['xyz'],points)
            np.testing.assert_array_equal(rows['rgb'],colors)

    def test_restore_validates_every_tensor_before_mutation(self):
        model=nn.Linear(2,2)
        model.register_buffer('calibration',torch.ones(1))
        before={n:v.detach().clone() for n,v in model.state_dict().items()}
        tensors={n:torch.zeros_like(v) for n,v in model.state_dict().items()}
        info={'trainable_names':['weight','bias']}
        tensors['calibration']=torch.ones(2)
        with self.assertRaises(ValueError):restore_adapter(model,tensors,info)
        for n,v in model.state_dict().items():self.assertTrue(torch.equal(v,before[n]))
        tensors['calibration']=torch.zeros(1)
        restore_adapter(model,tensors,info)
        self.assertTrue(all(torch.equal(v,tensors[n]) for n,v in model.state_dict().items()))

    def test_original_model_sources_are_unchanged(self):
        validate_model_sources()

if __name__=='__main__':unittest.main()
