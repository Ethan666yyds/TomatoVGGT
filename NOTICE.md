# Attribution and provenance

## TomatoVGGT / Tomato3D

Original contributions are by the TomatoVGGT contributors. The release citation lists Junge Sun, Qi Cheng, Yuan Li, Zhenghan Li, Jiaheng Wu and Jie Li in the author order of the associated manuscript. The release DOI identifies this dataset/software/model collection, not a published journal article.

## VGGT source code

VGGT: Visual Geometry Grounded Transformer, Jianyuan Wang, Minghao Chen, Nikita Karaev, Andrea Vedaldi, Christian Rupprecht and David Novotny, CVPR 2025.

- Copyright (c) Meta Platforms, Inc. and affiliates. All rights reserved.
- Source: https://github.com/facebookresearch/vggt
- Fixed source revision: `a288dd0f14786c93483e45524328726ab7b1b4ce`.
- Applicable source terms: `LICENSES/VGGT.txt`, including the Acceptable Use Policy.
- `src/tomatovggt/models/rgfu.py` ports the pinned DPT depth-head path and adds RGB-guided upsampling. The wrapper adds Q/V LoRA and strict model binding. Related model/RGB preprocessing paths retain upstream source terms. Original project source hashes are preserved so the selected checkpoint remains verifiable.
- Original contributions are identified by this notice; this release does not imply endorsement by Meta or the VGGT authors.

## VGGT-1B checkpoint

- Original checkpoint: https://huggingface.co/facebook/VGGT-1B
- Fixed revision: `860abec7937da0a4c03c41d3c269c366e82abdf9`.
- The model card at that revision declares `cc-by-nc-4.0`.
- Original base Safetensors SHA256: `f164acf60724910d8fe1578bb499d800850c7bb0948db7555c413f9fbe60467e`.
- The released TomatoVGGT adapter is derived from that checkpoint and retains the CC BY-NC 4.0 terms. It requires the separately downloaded original base weights. The existence of differently licensed VGGT checkpoints does not relicense this fixed checkpoint or the released adaptation.

## TomatoWUR data and calibration

Bart M. van Marrewijk, Tim van Daalen, Katarína Smoleňová, Bolai Xin, Gerrit Polder and Gert Kootstra. TomatoWUR: an annotated dataset of 3D tomato plants to quantitatively evaluate segmentation, skeletonisation, and plant trait extraction algorithms for 3D plant phenotyping.

- Dataset DOI: https://doi.org/10.4121/e2c59841-4653-45de-a75e-4994b2766a2f
- Source repository: https://github.com/WUR-ABE/TomatoWUR
- The DOI registry identifies the data license as CC BY-SA 4.0. The source repository's GPL-3.0 software license is a separate software license; no TomatoWUR source code is redistributed here.
- Public camera calibration is retained with source hashes under the synthetic archive's `provenance/` directory. Intrinsics are scaled for rendering and preprocessing; source world-to-camera poses are retained. Derived camera metadata identifies the transforms used.
- Original TomatoWUR RGB/reference files are not redistributed. The supplied real-data split retains the original identities and actual 28/6/10 train/validation/retrospective-test roles.

## Synthetic assets and release changes

The synthetic data card records native procedural Blender meshes, without purchased plant assets. Geometry, calibration, supervision, seeds and experiment scores are preserved. The distributed copies remove PNG text/EXIF metadata, clear Blender file-browser directory buffers, replace local absolute runtime paths, and rebind cache RGB lineage hashes to the pixel-identical sanitized files. `sanitization.json` and the original provenance records document those changes.

The result archive contains outputs from six methods. Their release does not distribute or relicense third-party model code or weights; rerunning a baseline requires its own upstream materials and terms. Real geometry is a reconstruction reference; synthetic geometry is ground truth.

## Original synthetic-data reuse

Original generated RGB images, plant meshes/scenes, depth/organ supervision, skeletons and traits are released under CC BY-NC 4.0 at the contributors' direction. Preserve attribution and the noncommercial condition. Public TomatoWUR calibration and its identifiable embedded camera elements retain CC BY-SA 4.0; they are not relicensed as noncommercial. See the component map for mixed-file scope.
