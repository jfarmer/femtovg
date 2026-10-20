#357 [OPEN] Exact-coverage fills on the OpenGL backend
The exact-coverage fill rasterizer (#327's fix) runs on the wgpu backend only; the OpenGL backend keeps the stencil-and-fringe path, so sub-pixel fills there stay a pixel wide (the 0.5 px bar at 1.45x its area, #327's table) and small text bolder than a browser's.

What the OpenGL port needs, matching `src/renderer/wgpu.rs`:

- One instance per edge: the edge's two endpoints ride a `Vertex` in the shared vertex buffer, and the vertex shader builds the sweep quad from `gl_VertexID` (0..6) and the instance. That is `glVertexAttribDivisor` + `glDrawArraysInstanced` (GL 3.3 / ES 3.0 / `ARB_instanced_arrays`) and a GLSL 1.30 / ES 3.00 vertex shader for `gl_VertexID`, so the accumulate program wants its own shader sources rather than `SELECT_SHADER` on `main-vs.glsl`. Without a base-instance draw, the attribute pointer offset moves to the fill's first edge before each draw.
- A signed-area accumulation target per render-target size: `R16F` with additive blending (`GL_ONE, GL_ONE`), which is core in GL 3.0 and ES 3.0 (`EXT_color_buffer_half_float` on ES 2). On a GL ES 2 device without it - a VideoCore IV - the fringe stays, so `supports_coverage_fills()` reports the capability from the context's version and extensions.
- The resolve is the glyph-mask draw with the atlas bound as the glyph texture and `glyphTextureType` 3 (nonzero) / 4 (even-odd): the `ENABLE_GLYPH_TEXTURE` block of `main-fs.glsl` gets the two cases `shader.wgsl` has, including the discard at zero coverage that keeps composite operations to the pixels a shape covers.
- The render loop switches to the atlas framebuffer for a batch's accumulates (clearing on the batch's first) and back to the target for the resolve, as the wgpu loop does around `AccumulateCoverage` / `CoverageFill`.

Verification: `tests/coverage_fill_wgpu.rs` ported to a headless GL context, and the harness A/B against the wgpu renders (both exact, so bit-identical up to float16 rounding).

--- comments: 0

