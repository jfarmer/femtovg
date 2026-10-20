#13 [OPEN] Investigate using exact coverage for antialiasing
[nanovgXC](https://github.com/styluslabs/nanovgXC) shows how to adapt Pathfinder's exact coverage calculation method to NanoVG. It minimally requires support for an F32 single channel render target, and has some optional paths to use the shader framebuffer fetch (which is supported on Intel gfx, but not on NVIDIA's PC GPUs) or atomic image operations.

This method's most noticeable impact is on glyph rasterization when compared with standard nanovg. I don't think it provides any new capabilities (like path masking) compared to the current nanovg method.
--- comments: 0

