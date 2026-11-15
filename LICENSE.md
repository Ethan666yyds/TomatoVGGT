# Component licenses

Copyright (c) 2026 TomatoVGGT contributors, for their original contributions.

This release contains separately licensed components. Licenses apply to the components identified below; they are not alternatives that can be chosen for the entire release.

| Component | Applicable terms |
|---|---|
| Independently authored software, command-line tools, tests and original software contributions | MIT, in `LICENSES/MIT.txt` |
| VGGT-derived model code and retained upstream implementation material, including the model adapter and RGB preprocessing paths | Upstream VGGT License v1 (29 July 2025), in `LICENSES/VGGT.txt`; original author contributions additionally carry MIT permissions without relicensing upstream material |
| `weights/tomatovggt.safetensors` and adaptations derived from the pinned original VGGT-1B checkpoint | CC BY-NC 4.0, in `LICENSES/CC-BY-NC-4.0.txt`; attribution and noncommercial restriction retained from the original checkpoint |
| Original Tomato3D synthetic RGB images, plant geometry, generated supervision/labels, skeletons and traits | CC BY-NC 4.0, in `LICENSES/CC-BY-NC-4.0.txt`; noncommercial reuse only, for rights held by the contributors |
| Released result assets, dataset descriptions and original figures/documentation | CC BY-SA 4.0, in `LICENSES/CC-BY-SA-4.0.txt`, for rights held by the contributors, with upstream attribution and terms retained |
| TomatoWUR calibration included in synthetic assets and any TomatoWUR-derived reference material | Upstream CC BY-SA 4.0; see `NOTICE.md` |

The source package's SPDX expression `MIT AND LicenseRef-VGGT` describes its software components. It is not a permissive-license grant for the model weights, datasets or upstream dependencies.

The original VGGT base model and original TomatoWUR data are obtained separately from their respective providers. No ownership of, or new rights to, third-party materials are asserted. Third-party baseline software and weights are not licensed by this release.

When redistributing a component, include the applicable license text and attribution. When distributing the combined release, retain this map and the complete `LICENSES/` directory. See `RELEASE_NOTICE.md` for how the notices accompany the archive files.

Camera/calibration content retains the upstream CC BY-SA 4.0 terms, including `cameras.json`, calibration/provenance files and embedded intrinsic/extrinsic camera arrays or scene-camera elements. Original plant/image/supervision content in a mixed file retains CC BY-NC 4.0. The noncommercial grant does not impose new restrictions on the upstream calibration components. Licenses on separately released result/figure files do not grant commercial rights to the original synthetic dataset as a whole.
