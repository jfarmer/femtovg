#410 [OPEN] A self-crossing fill draws the lobe wound against its contour a pixel too wide
A contour that crosses itself so that its lobes wind in opposite directions, a bow-tie, has one lobe drawn about a pixel wider than it is, against Chromium and Firefox alike. A pentagram, which crosses itself with every region wound alike, draws as they do.

![femtovg, Chromium, Firefox and femtovg against Chromium, for two bow-ties and a pentagram](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/issue-bowtie-fringe.png)

Pixels more than 20 levels off Chromium 131 at 1x (master 9f5ad26, WGPU): the 104 x 80 bow-tie 685, the 40 x 40 one 274, the pentagram 26, the edge antialiasing every fill differs by. Across the wide lobe's edge, the green channel (255 is white): Chromium `255 255 255 255 107 34`, femtovg `255 255 255 107 34 34`.

`PathCache::expand_fill` turns each contour round, or not, by the sign of its whole area ([`polygon_area`](https://github.com/femtovg/femtovg/blob/9f5ad26/src/path/cache.rs#L759)), then offsets the fill and fringe vertices along each point's miter for that orientation. A lobe wound against the sign gets the offset on the wrong side; with equal lobes, rounding picks which. Both backends draw these vertices.

The extracted reftest `18-hard-mask-composite-concave-winding/hard-mask-figure-eight` (a clipped bow-tie, then a concave fill) fails against Chromium by this edge, 142 pixels at 1x, not by winding left in the stencil. #408's thin-fill masks draw a small bow-tie exactly, since its lobes' areas cancel and it measures 0 px wide, but one whose bounds pass 65,536 pixels keeps the fringe.

Probes: [demo-assets harness/bowtie-fringe](https://github.com/rebeckerspecialties/femtovg/tree/demo-assets/harness/bowtie-fringe).

--- comments: 0

