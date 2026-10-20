#305 [OPEN] wgpu backend costs ~0.5ms of GPU-process time per drawn element on wasm
On wasm the wgpu backend spends roughly 0.5ms of GPU-process time per drawn
element. A page with 200 rectangles presents at 8fps, where the same scene on
the GL backend holds 144fps in the same browser on the same machine.

## Measurements

Chrome on a 144Hz display, NVIDIA discrete GPU, window in the foreground. The
figures are `Display::DrawAndSwap` and GPU-process time attributed to the page's
renderer pid, both read from a Chrome trace. The scene is N static rounded
rectangles plus one animated rectangle to drive redraws, which is what
`examples/many_rects.rs` in #304 renders.

| rectangles | wgpu | GL |
| --- | --- | --- |
| 0 | 4.25ms | 0.28ms |
| 200 | 103.06ms, 8.1fps | 0.41ms, 144fps |
| 600 | | 0.71ms, 144fps |
| 1000 | 434.46ms, 2.0fps | 1.02ms, 144fps |

The growth is linear in the number of elements: 0.57us at 50 rectangles, 0.53us
at 200, 0.43us at 1000.

## What it is not

Rasterisation. Shrinking the viewport by forty times the pixels leaves the cost
unchanged, and the same holds for corner radius and element type.

Driver work. At 200 rectangles `vkQueueSubmit` accounts for 0.2ms per frame and
`CommandBufferVk::RecordCommands` for another 0.2ms, against a frame costing
over 100ms. The time sits inside Dawn's CPU side, in `Queue::Submit` and
`WebGPUDecoderImpl::HandleDawnCommands`, outside any traced child span.

## Where it comes from

On a bind group cache miss, `BindGroupState::materialize` and
`create_binding_resource_and_sampler` create a uniform buffer, two samplers, two
texture views and a bind group. On wasm each of those crosses the JS boundary
into the GPU process to be allocated and validated, and `create_buffer_init` is
alloc, map, copy and unmap on top.

The cache misses on nearly every draw. It is a single slot compared with
`PartialEq` over the whole 224 byte `UniformArray` (`wgpu.rs`, in
`update_renderpass`), so two rectangles of the same colour at different
positions have different paint matrices and miss.

Counted in the browser by wrapping `GPUDevice.prototype`, a page drawing 200
rectangles creates per frame:

| | rects=0 | rects=200 | per rectangle |
| --- | --- | --- | --- |
| buffers | 4 | 204 | 1.0 |
| bind groups | 3 | 203 | 1.0 |
| samplers | 4 | 404 | 2.0 |
| texture views | 7 | 407 | 2.0 |

Two samplers and two views per rectangle are of the 1x1 empty texture and never
vary with the scene.

For contrast, `opengl.rs` calls `set_uniforms` once per command, outside the
drawable loop, and that is one `glUniform4fv` plus two `glBindTexture` with no
allocation.

## Notes

Measured only on wasm through Chrome. Native was not measured, and the same
allocations should be much cheaper there.

I have a branch that addresses this and can open it if the approach is welcome,
but I would rather hear first how you would want it fixed.

--- comments: 0

