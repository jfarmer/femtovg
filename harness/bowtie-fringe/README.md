# A self-crossing fill whose lobes wind against each other

`PathCache::expand_fill` turns each contour round, or not, by the sign of its
whole area (`polygon_area`), and offsets its fill and fringe vertices along
each point's miter for that orientation. A contour that crosses itself so that
its lobes wind in opposite directions - a bow-tie - has the lobe wound against
the sign offset to the wrong side: drawn a pixel wider than it is. When the
lobes are equal, rounding picks the lobe.

- `bowtie.svg`, `bowtie-big.svg`: one contour each, the two lobes wound
  against each other. `pentagram.svg`: one contour crossing itself with every
  region wound alike (the control).
- `../../issue-bowtie-fringe.png`: femtovg (master 9f5ad26, WGPU) | Chromium 131
  | Firefox | femtovg against Chromium, at 1x. Pixels more than 20 levels off
  Chromium: bow-tie 685 (the 104 x 80 one), 274 (40 x 40); pentagram 26, the
  edge antialiasing every fill differs by. Firefox agrees with Chromium within a
  pixel.

The reftest suite's `18-hard-mask-composite-concave-winding/hard-mask-figure-eight`
fails against Chromium by this edge (142 pixels at 1x), not by winding left in
the stencil.
