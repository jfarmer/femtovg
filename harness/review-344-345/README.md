Review probes for femtovg #344 and #345 against master 056c66a6.

- `pr345_shortcut_vs_general_fill.rs.txt`: a 48 x 48 rect filled with a repeating 2 x 2 image under an image transform
  (identity, scale, shear, rotate), through the non-AA blit shortcut, under a clip_path, and as a pentagon that takes the
  general fill; counts the interior pixels (34 x 34) that differ. Non-AA: 0 for identity and scale, 576 for shear and 771
  for rotation (both rect paths); anti-aliased: 0 everywhere.
- `master_shear_shortcut.rs.txt`: the same mismatch on master with no new API: a parallelogram under a canvas shear that is an
  axis-aligned rect on screen, plain image paint, non-AA: 14 of 576 interior pixels differ from the same shape with a notch.
