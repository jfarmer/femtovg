#151 [OPEN] Weird Stencil Stroke Artifacts
Hi! I wanna simulate a text marker and have found a method `with_stencil_stroke` for a Paint to make it overlap in the same path as you can see in the pictures. but now it leaves some weird artifacts behind when i move slowly.

Stencil Stroke = `true` (seems like the default)
![image](https://user-images.githubusercontent.com/82600264/221202211-b5e66f26-743d-422e-a44d-b26f8edf1fc7.png)

Stencil Stroke = `false`
![image](https://user-images.githubusercontent.com/82600264/221202465-7122c531-e9ec-4020-9198-863c0f4ba315.png)

Is there a way to still have that overlapping without having those artifacts? Thanks :d
--- comments: 5
> DasLixou: Ok so i just need to limit the path segments. I now check if the distance between the last point is greater than the line width and only then i add a new one
> DasLixou: But is there a better way to fix this?

> porky11: To me it looks like the problem is on your side.
For debugging purposes you could draw small points or lines to see where the exact points are.
I assume, they are not in a smooth line.
You could try to force a minimal distance on the points you create.
> DasLixou: Yeah that is what I am doing now. I require a minimum distance of the pencil width so that it doesn’t overlap
> DasLixou: > To me it looks like the problem is on your side. For debugging purposes you could draw small points or lines to see where the exact points are. I assume, they are not in a smooth line. You could try to force a minimal distance on the points you create.

![image](https://user-images.githubusercontent.com/82600264/227790142-5b18245d-deb9-445c-85ab-b25e63f98c56.png)

Played with it a little more, looks like its a problem with the edges.
My paint:
```rust
Paint::color(Color::rgbaf(
    65. / 255.,
    212. / 255.,
    215. / 255.,
    100. / 255.,
))
.with_stencil_strokes(false)
.with_line_width(12.)
.with_line_cap(LineCap::Square)
.with_line_join(vizia::vg::LineJoin::Bevel);
```
