Fixes #327. Supersedes #358. Based on #407, which even-odd rings need. #409 carries the uploads in the frame's own command buffer.

The fringe that antialiases a fill's edges gives it about a pixel of ink however thin it is: a sliver a tenth of a pixel wide comes out nearly eight times as dark as its area, a mark at thumbnail size up to a quarter too dark. A thin fill - mean width (twice its area over its perimeter, holes taken off) under two pixels, or under one if every contour is convex; bounds at most 65,536 pixels; an operation that coverage bounds - is now rasterized on the CPU by the clip masks' exact-area coverage into a one-byte atlas and drawn as one quad through `GlyphTexture::AlphaMask`, so paint, scissor and clips apply as they do to text, on both backends. A convex contour a pixel wide and more keeps its fringe, which draws a rectangle exactly (decorations, borders, separators). Masks are found again by request or by outline, at most 256 are made a frame, and the atlas grows each side only as its masks need, up to 2048 or the backend's limit, stores tall masks transposed, keeps on the CPU only the rows in use, and shrinks once a moving scene needs less. `Canvas::set_thin_fill_masks(false)` turns it off.

**Evidence.** Canvas scenes against the 8x area reference (Chromium 131 at 8x, averaged); OpenGL and WGPU are pixel-identical:

![scenes](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/pr-thin-fill-masks-scenes.png)

| pixels > 20 levels off the area | master | this PR | Chromium 1x |
|---|---:|---:|---:|
| slivers 0.12 to 0.8 px | 244 | 0 | 380 |
| rings 0.5 px | 584 | 0 | 23 |
| hairlines 0.3 px, crossing | 2,310 | 0 | 1,232 |
| crescent 0.6 px | 339 | 0 | 16 |
| outline 0.4 px around a body | 544 | 0 | 0 |

#327's New York Times marks: at 20 px +9 to +101 % over Chromium's ink on master, within 2 % here; at 50 px the tile logo +23 -> +2 % and the Cooking wordmark +14 -> 0 % against Chromium and Firefox alike, and both now match WebKit pixel for pixel (45 and 78 pixels off before).

Corpus, 12,670 frames (ten framings, from a tenth of the fit to four times it, 1080p and 240p): 1,522 change. On the 579 with an area reference, pixels beyond 20/255 of it 239,663 -> 185,912 (Firefox 141,008, GPU Chromium 150,393, software Chromium 199,649); 523 frames nearer, 29 further. The furthest from it is an image drawn as 65,536 unit squares, which conflates as Chromium and Firefox do (+35,018 px, #411); of the other 28 (+1,163 px), 21 land nearer Chromium or Firefox, where an exact thin fill meets a draw beside it and each is composited by its own coverage (the fox row below), 3 have no browser frame, and 4 move 4 to 20 px in text and soft edges that both builds draw unlike both references. Against the browsers themselves, pixels off each fall 37 % for Firefox (464 frames nearer, 23 further), 27 % for Chromium (451, 24) and 26 % for WebKit (115, 1); the WPT reftests `fill-path-subpixel-sliver-control` and `hard-mask-figure-eight` go from 225 and 142 pixels off to 0 and 2 against Chromium and WebKit, and to 0 and 52 against Firefox.

![corpus at 1x and up](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/pr-thin-fill-masks-corpus.png)
![corpus below 1x](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/pr-thin-fill-masks-small.png)

**Tests:** masks found again, the 256 a frame, a moving scene's atlas starting over, the atlas (growth by side, the backend's limit, the first placement, room left after a miss, transposition, the rows kept, shrinking), degenerate contours, and which fills are thin; on WGPU, a sliver's and a ring's area, the paint, the scissor and clips, masks kept as others are made and as the atlas grows, and a tall sliver drawn as the wide one turned on its side.

**Cost**, the masks on against off: still frames on an M4 -1.9 % in sum (median -0.7 %), moving ones -0.1 % (median -0.1 %, worst +18 %). In motion, every mask made again each frame, the render thread's efficiency-core cycles over eight thin-fill files: +5.4 % on an iPhone XS Max, +5.8 % on an iPhone SE, the worst diners at 1080p (+27 to +29 %); with #409 +6.1 and +6.4 %. Footprint within 0.3 MiB once the atlas settles (+0.4 to 1.5 MiB while the first 1080p files grow it); GPU time on the SE at 1080p -1 %. Reusing masks while a scene pans is #412.
