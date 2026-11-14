import os,sys,unittest
import torch
from torch.nn import functional as F
from tomatovggt.models.rgfu import RGFUHead,RGBGuidedUpsample,guided_bilinear

class RGFUTests(unittest.TestCase):
 def test_zero_guidance_is_exact_bilinear_and_has_gradients(self):
  for shape,size in [((3,4),(5,7)),((1,4),(5,1)),((296,296),(518,518))]:
   x=torch.randn(1,2,*shape)
   for align in [False,True]:
    self.assertTrue(torch.equal(guided_bilinear(x,torch.zeros(1,4,*size),align_corners=align),F.interpolate(x,size=size,mode='bilinear',align_corners=align)))
  m=RGBGuidedUpsample();x=torch.randn(1,3,4,4,requires_grad=True)
  out=m(x,torch.rand(1,3,8,8));(out*torch.randn_like(out)).sum().backward()
  self.assertEqual(sum(p.numel() for p in m.parameters()),1028)
  self.assertGreater(float(m.predict[-1].weight.grad.abs().sum()),0)
 def test_known_weighted_center_and_gradcheck(self):
  x=torch.tensor([[[[1.,2.],[3.,4.]]]],dtype=torch.float64,requires_grad=True)
  logits=torch.zeros(1,4,3,3,dtype=torch.float64,requires_grad=True)
  with torch.no_grad():logits[0,0,1,1]=torch.tensor(2.,dtype=torch.float64).log()
  self.assertAlmostEqual(float(guided_bilinear(x,logits)[0,0,1,1].detach()),2.2,places=12)
  self.assertTrue(torch.autograd.gradcheck(guided_bilinear,(x,logits)))
 def test_extreme_logits_preserve_boundaries_and_reject_nan(self):
  x=torch.randn(1,2,3,3);logits=torch.randn(1,4,5,5)*10000
  y=guided_bilinear(x,logits);self.assertTrue(torch.isfinite(y).all())
  torch.testing.assert_close(y[:,:,0,0],x[:,:,0,0]);torch.testing.assert_close(y[:,:,-1,-1],x[:,:,-1,-1])
  logits[0,0,0,0]=torch.nan
  with self.assertRaises(FloatingPointError):guided_bilinear(x,logits)

@unittest.skipUnless(os.environ.get('VGGT_ROOT'),'set VGGT_ROOT for pinned upstream DPT parity')
class DPTParityTests(unittest.TestCase):
 def test_vendor_head_parity_rng_and_chunks(self):
  sys.path.insert(0,os.environ['VGGT_ROOT'])
  from vggt.heads.dpt_head import DPTHead
  torch.set_num_threads(1)
  base=DPTHead(dim_in=16,features=8,out_channels=[8]*4,output_dim=2,intermediate_layer_idx=[0,1,2,3],activation='exp').eval()
  images=torch.rand(1,2,3,518,518);tokens=[torch.randn(1,2,1370,16) for _ in range(4)]
  state=torch.get_rng_state().clone();model=RGFUHead(base).eval()
  self.assertTrue(torch.equal(state,torch.get_rng_state()))
  with torch.no_grad():
   expected=base(tokens,images,1,frames_chunk_size=1);got=model(tokens,images,1,frames_chunk_size=1)
   for a,b in zip(expected,got):torch.testing.assert_close(a,b,atol=1e-6,rtol=1e-6)
   other=model(tokens,images,1,frames_chunk_size=None)
   for a,b in zip(got,other):torch.testing.assert_close(a,b,atol=1e-5,rtol=1e-5)
