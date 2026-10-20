A coverage mask adds each edge's signed area into the cells it crosses and folds the sum by the fill rule, which is exact only where a pixel sees at most two windings, one apart. An even-odd ring thinner than a pixel with both circles wound alike puts 0, 1 and 2 into the pixels it crosses, and its hole counts as coverage: a clip to a ring 0.4 px wide covered 113.4 px for its area of 74.9. Even-odd does not depend on direction, so a hole's contour is now wound against the contours around it, as `expand_fill` already winds them for its fringe, and nested contours wind 0 or 1. Non-zero is left alone: there the direction is the meaning.

![even-odd clips](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/pr-even-odd-masks.png)

Clips filled through with navy, top-right quarter at 10x, against the 8x area reference (Chromium 131 at 8x, averaged); OpenGL and WGPU are identical before and after. Pixels more than 20 levels off the area over each whole scene: the ring 136 -> 0, a non-zero ring as control 0 -> 0, a disc whose off-centre hole comes within 0.2 px of its edge 48 -> 0.

No corpus frame moves (11,403 compared). The thin-fill masks of #408 rasterize with the same code and need this for even-odd rings.
