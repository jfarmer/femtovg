Fixes #327. Supersedes #358. Based on #407, which even-odd rings need; the last commit is this PR's.

The fringe that antialiases a fill's edges gives the fill about a pixel of ink across however thin it is: a sliver a tenth of a pixel wide comes out nearly eight times as dark as its area, a 0.3 px hairline nearly three times. A fill whose mean width (twice its area over its perimeter, a hole's area taken off under the fill's rule) is under a pixel, whose bounds span at most 65,536 pixels and whose operation coverage bounds is now rasterized on the CPU by the clip masks' exact-area coverage into one 2048 x 2048 one-byte atlas, and drawn as a quad through `GlyphTexture::AlphaMask`: paint, scissor and clips apply as they do to text, on both backends, with no shader change. A mask is found again by request (fill rule, path, transform, tolerances and target size, bit for bit) or by outline (to 1/256 px from its corner); a frame uploads the rectangle its new masks span; at most 256 are made a frame, as Graphite's `RasterPathAtlas`, past which a thin fill keeps its fringe; the atlas starts over when it fills or when a frame finds none of the masks the frame before made. `Canvas::set_thin_fill_masks(false)` turns it off.

**Canvas scenes** against the 8x area reference (Chromium 131 at 8x, averaged); OpenGL and WGPU are pixel-identical, before and after:

![scenes](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/pr-thin-fill-masks-scenes.png)

Pixels more than 20 levels off the area, master -> this PR (Chromium at 1x): slivers 244 -> 0 (380), rings 584 -> 0 (23), hairlines 2,310 -> 0 (1,232), crescent 339 -> 0 (16), outline around a body 544 -> 0 (0). The 15 left under the triangle clip are where a sliver runs along the clip's edge inside a pixel: the clip's coverage multiplies the sliver's, as it multiplies every draw's.

**Corpus**, 11,403 frames: 1,094 change, 293 of them at 1x and up. The 397 with an area reference: pixels beyond 20/255 of the area 139,475 -> 83,122 (WebKit 83,048, GPU Chromium 104,960, Firefox 62,194 on the same frames), 359 frames nearer and 15 further; at 1x and up 86,216 -> 61,964, 101 nearer and 3 further by 1 to 6 px.

![corpus at 1x and up](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/pr-thin-fill-masks-corpus.png)
![corpus below 1x](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/pr-thin-fill-masks-small.png)

The further frames are where an exact thin fill meets a draw beside or over it, each composited by its own coverage (fox-with-box at 0.5x 697 -> 899; software Chromium 908, Firefox 916), and one icon whose light sliver had half hidden the over-inked thin tip of the thick path beneath it: a whole path's mean width does not see a thin part of a thick path.

**Cost.** One binary with the masks on and off, the 365 files whose frames change, 1x and 1080p: still -1.1 % in sum, median frame +0.1 %; every frame moved by 0.37 px, so that each mask is made again each frame, -0.2 % in sum, median +0.1 %. Files whose frames do not change +0.1 %, median 0.0 %; card pages +0.0 to +0.2 % instructions. In motion the frames with the most thin fills pay for remaking them: diners at 1080p +0.28 ms a frame (13 masks, 75,000 px), the tiger at 1x +0.24 ms, most of it the rasterizer sorting cells by row. Draft while that rasterizer, the clip masks' too, is made cheaper against profiles on the M4's and an Apple TV 4K's efficiency cores.
