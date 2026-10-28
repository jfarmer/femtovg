#411 [OPEN] Abutting fills thinner than a pixel let the background through (conflation)
Babylon's `vertex-pulling-normals-uvs-colors-tangents` test, captured as SVG ([corpus/babylon](https://github.com/rebeckerspecialties/femtovg/blob/demo-assets/corpus/babylon/vertex-pulling-normals-uvs-colors-tangents__1.svg)), is an image drawn as 256 x 256 unit squares, each a path with its own colour. Fitted into 240 px, each square is 0.94 px across, so almost every pixel holds the edges of two to four squares. Each square is antialiased and composited on its own: a pixel split between two squares gets the second square's share over the first's result, not the two shares together, so some of the white background stays in it. The image comes out washed out, with a darker grid every 16 px where the squares' edges fall on pixel edges.

![master, #408, Chromium and the 8x area reference](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/issue-mesh-conflation.png)

| 426 x 240 frame | pixels beyond 20/255 of the area reference |
|---|---:|
| master (fringe fills) | 14,390 (14 %) |
| #408 (thin fills through exact-area masks) | 49,408 (48 %) |
| Chromium 131 | 50,388 (49 %) |
| Firefox 158 | 50,806 (50 %) |

With #408, femtovg draws it as Chromium and Firefox do: 0.03 % of the frame is beyond 20/255 of either. Master's fringes overlap the neighbouring squares and cover the background, which lands nearer the area reference by accident. The area reference (Chromium at 8x, averaged) has no conflation because each of its samples falls inside one square.

Getting the area's result means weighting the colours of the fills that share a pixel by their area, which a multisampled target does at its sample count. Neither browser does that at 1x, so this goes beyond matching them. The same pattern shows up in QR codes and pixel art drawn as rects at fractional scales, heat maps and charts of adjacent cells.

--- comments: 0

