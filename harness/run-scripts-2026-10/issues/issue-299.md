#299 [OPEN] WGPU renderer panics uploading an HtmlImageElement whose attributes exceed its natural size
## Summary

`ImageSource::HtmlImageElement` means a different size to each backend, and the WGPU renderer turns the disagreement into a panic. Uploading an SVG-backed `<img>` whose width/height attributes have been enlarged for hidpi output aborts the process:

```
panicked at wgpu-29.0.4/src/backend/webgpu.rs:2697:14:
called `Result::unwrap()` on an `Err` value: JsValue(OperationError:
Failed to execute 'copyExternalImageToTexture' on 'GPUQueue':
Copy rect is out of bounds of external image
```

## Where the disagreement comes from

`ImageSource::dimensions()` reads `element.width()` for an `HtmlImageElement`, so it returns the attribute size. The OpenGL renderer uploads through `tex_sub_image_2d_with_html_image`, and the browser rasterizes an SVG at those attributes, so the attribute size is the truth there. The WGPU renderer passes the same number to `copy_external_image_to_texture` as the copy extent, but WebGPU takes the source size of an `HTMLImageElement` from its natural size and validates the rect against that. Enlarging the attributes therefore produces a rect larger than the source.

Setting the attributes is how a caller asks for a sharper rasterization of a scalable source, and it works under WebGL. Slint does exactly this for hidpi displays, which is how I ran into it.

## Evidence that the attributes buy nothing on WebGPU

This page uses a 16x16 SVG with its attributes set to 20x20, matching a 1.25 scale factor:

```html
<script type="module">
const SVG = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
  <rect width="16" height="16" fill="black"/><path d="M0 16 L16 0" stroke="white" stroke-width="1"/></svg>`;
const img = new Image();
img.src = URL.createObjectURL(new Blob([SVG], { type: "image/svg+xml" }));
await img.decode();
img.width = 20; img.height = 20;
console.log(img.naturalWidth);                // 16

const device = await (await navigator.gpu.requestAdapter()).requestDevice();
const tex = (n) => device.createTexture({ size: [n, n], format: "rgba8unorm",
  usage: GPUTextureUsage.COPY_DST | GPUTextureUsage.COPY_SRC | GPUTextureUsage.RENDER_ATTACHMENT });

device.queue.copyExternalImageToTexture({ source: img }, { texture: tex(20) }, [20, 20]);
// OperationError: Copy rect is out of bounds of external image

device.queue.copyExternalImageToTexture({ source: img }, { texture: tex(16) }, [16, 16]);
// succeeds
</script>
```

The 16x16 copy succeeding is the part that matters: WebGPU reads the natural-size rasterization whatever the attributes say. Going through a canvas does reach the resolution the caller asked for:

```js
const cv = document.createElement("canvas");
cv.width = cv.height = 20;
cv.getContext("2d").drawImage(img, 0, 0, 20, 20);
device.queue.copyExternalImageToTexture({ source: cv }, { texture: tex(20) }, [20, 20]); // succeeds
```

Reading that texture back shows 3 distinct shades along the diagonal, so the SVG is rasterized at 20x20 rather than a 16x16 bitmap being stretched.

Observed with Chrome 150.0.7871.114 on Linux at `devicePixelRatio` 1.25, wgpu 29.0.4, femtovg 0.25.1. At a scale factor of exactly 1 the two sizes coincide and nothing fails, so emulated viewports pinned to dpr 1.0 do not show it.

## What I propose

A canvas carries the same size for both backends, so an `ImageSource::HtmlCanvasElement` variant gives callers a way to rasterize a scalable source at the size they want and upload it without either backend guessing. glow already has `tex_sub_image_2d_with_html_canvas` and wgpu already has `ExternalImageSource::HTMLCanvasElement`, so the plumbing is short. PR follows.

That leaves the existing `HtmlImageElement` path still able to panic when a caller enlarges the attributes. Clamping the copy extent to the element's natural size in the WGPU renderer would contain it, at the cost of silently uploading a smaller image than the caller asked for. Returning `ErrorKind::ImageUpdateOutOfBounds` instead would make the mismatch visible, which matches how `update_image` reports a destination overflow today. I have the clamp written and can send either one, so I would rather hear which you prefer than pick for you.

#277 fixed two other problems in this same upload path and left the extent untouched, so this predates that change rather than following from it.

--- comments: 1
> tronical: I think it would be best if the API just worked. So if the dimensions don't match, create an intermediate ImageBitmap that should cause the SVG to get rasterized to the right size. What do you think?
