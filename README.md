# darkroom-as-code

**A reproducible RAW photo pipeline, where every edit is a version-controlled recipe.**

Most photo editors store edits in opaque catalogs or GUI state. `darkroom-as-code` treats a photograph the way infrastructure-as-code treats a server: the RAW file is immutable input, the edit is a declarative recipe in Git, and the print is a deterministic build artifact. If you change your mind about a crop a year from now, you change one line and re-render.

The project is built around a review loop: for each photo, two or three distinct interpretations are written as candidate recipes and rendered as small previews and a side-by-side contact sheet. The photographer chooses one and refines it, and the chosen recipe then renders a full-resolution, print-ready file locally.

> **Status:** early development. The design below is the plan; see [Roadmap](#roadmap) for what exists today.

---

## Why

- **Reproducible.** Same RAW + same recipe → same output, bit for bit.
- **Reviewable.** Edits are text, so they diff, branch and revert like code.
- **Local-first.** Full-resolution RAWs and print files never leave the machine. Only downscaled previews, with location metadata stripped, are ever used for review.
- **Batchable.** A "base look" for a whole shoot is just a recipe applied to many photos.

## How it works

```
 RAW (read-only)          recipe.yaml                 outputs
 ┌──────────────┐   ┌─────────────────────┐   ┌──────────────────────────┐
 │ IMG_4821.NEF │──▶│ develop → ops → out │──▶│ preview.jpg  (≤1600 px)  │
 └──────────────┘   └─────────────────────┘   │ contact sheet (A | B | C)│
        │                                     │ print.tif (16-bit, full) │
        ▼                                     └──────────────────────────┘
  rawpy / LibRaw:                        float32, linear working space
  demosaic → linear 16-bit                until the final tone map
```

1. **Develop:** decode the RAW into linear, scene-referred float32 data (white balance, base exposure).
2. **Ops:** an ordered list of small, pure operations: crop and straighten, tone, colour balance, masked local adjustments (sky, luminance ranges), dodge and burn, noise reduction, sharpening, spot removal.
3. **Output:** tone-map to display/print, convert colour space, embed the ICC profile, and write a preview JPEG or a 16-bit print TIFF.

## A recipe

```yaml
photo: 2025-06-coast/IMG_4821.NEF
candidate: b
intent: "Moody: darker sky, warm light on the cliffs, 5:4 for a 40×50 frame"

develop:
  white_balance: camera
  exposure_ev: -0.3

ops:
  - op: crop
    aspect: "5:4"
    rotate_deg: -1.5
  - op: tone
    shadows_ev: 0.8
    highlights_ev: -0.6
  - op: local_exposure
    mask: { type: sky, feather: 0.03 }
    exposure_ev: -0.5
  - op: color_balance
    highlights: { hue: 45, chroma: 0.04 }
  - op: sharpen
    amount: 0.6
    radius_px: 1.2

output:
  tone_map: sigmoid
  contrast: 1.15
```

## Planned usage

```bash
uv sync

# Configure where your RAW library lives (local, gitignored)
cp darkroom.example.toml darkroom.toml

darkroom preview  recipes/IMG_4821/candidate_b.yaml   # → out/previews/
darkroom compare  recipes/IMG_4821/                   # → contact sheet of all candidates
darkroom print    recipes/IMG_4821/chosen.yaml        # → out/print/, 16-bit TIFF
darkroom sheet    2025-06-coast/                      # → culling contact sheet for a folder
```

## Roadmap

- [x] **M0:** project scaffold: uv, CLI skeleton, config, CI (ruff + pytest)
- [ ] **M1:** RAW develop + preview export (rawpy → linear float32 → sRGB JPEG)
- [ ] **M2:** core ops: crop/rotate, exposure, tone, colour balance, sharpen, denoise
- [ ] **M3:** recipe schema + validation, candidate workflow, contact sheets
- [ ] **M4:** masks and local adjustments (sky, luminance, gradients), spot removal
- [ ] **M5:** print export: 16-bit TIFF, embedded ICC, aspect/size presets for frames
- [ ] **M6:** batch rendering and shared base looks per shoot

## Design principles

- RAW files are **never modified**. The library is mounted read-only into the pipeline.
- Recipes are the **single source of truth**. Rendered files are disposable build artifacts.
- Every op is a **pure function** of image + parameters, so it can be tested on synthetic images.
- Processing stays in **float32 linear light** until the final output transform.
- **No photos in the repository.** Tests use synthetic images; personal photos stay local.

## Tech stack

Python 3.12 · [uv](https://docs.astral.sh/uv/) · [rawpy](https://github.com/letmaik/rawpy) (LibRaw) · NumPy · OpenCV · scikit-image · tifffile · Pillow · Pydantic · Typer · pytest · ruff

## License

MIT
