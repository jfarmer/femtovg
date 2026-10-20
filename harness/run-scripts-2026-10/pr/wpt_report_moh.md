290 pairs measured of 290; threshold 0.15 % px>20 on moh
66 pairs above threshold

## 01-clip-and-blend (1)
| test | framing | base | ab | pyr | mo | moh | ref vs Chromium | self reftest | Chromium self |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| blend-clip-rounded-parent | z2 | 0.43 | - | - | 0.43 | 0.43 | 0.42 | 0.17 | 0.20 |

## 03-mask-and-blend (1)
| test | framing | base | ab | pyr | mo | moh | ref vs Chromium | self reftest | Chromium self |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| blend-mask-circle-difference | z2 | 0.26 | - | - | 0.26 | 0.26 | 0.26 | 0.00 | 0.00 |

## 05-filter-clip-regressions (2)
| test | framing | base | ab | pyr | mo | moh | ref vs Chromium | self reftest | Chromium self |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| filter-clip-under-blur | z4 | 0.00 | 0.00 | 0.87 | 0.87 | 0.87 | 0.87 | 0.00 | 0.00 |
| filter-blur-clip-ancestor | z1 | 0.27 | 0.27 | 0.27 | 0.27 | 0.27 | 0.00 | 0.00 | 0.27 |

## 06-svg-compositing-primitives (1)
| test | framing | base | ab | pyr | mo | moh | ref vs Chromium | self reftest | Chromium self |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| blend-plus-lighter-isolated | z4 | 42.10 | - | - | 42.10 | 42.10 | 0.00 | 42.10 | 0.00 |

## 07-zero-area-collinear-fills (1)
| test | framing | base | ab | pyr | mo | moh | ref vs Chromium | self reftest | Chromium self |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| fill-path-subpixel-sliver-control | z4 | 0.25 | - | - | 0.25 | 0.25 | 0.25 | 0.00 | 0.00 |

## 11-blend-gradients-and-clips (2)
| test | framing | base | ab | pyr | mo | moh | ref vs Chromium | self reftest | Chromium self |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| blend-clip-path-gradient-difference | z2 | 0.57 | - | - | 0.57 | 0.57 | 0.57 | 0.00 | 0.00 |
| blend-clip-path-nested-overlay | z2 | 0.40 | - | - | 0.40 | 0.40 | 0.40 | 0.00 | 0.00 |

## 12-blend-filter-chains (4)
| test | framing | base | ab | pyr | mo | moh | ref vs Chromium | self reftest | Chromium self |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| filter-chain-blur-feblend-sourcealpha | z4 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 0.00 | 100.00 | 0.00 |
| filter-chain-colormatrix-feblend-screen | z4 | 100.00 | - | - | 100.00 | 100.00 | 0.00 | 100.00 | 0.00 |
| filter-chain-offset-blur-feblend | z4 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 0.00 | 100.00 | 0.00 |
| filter-subregion-chain-feblend | z4 | 100.00 | - | - | 100.00 | 100.00 | 0.00 | 100.00 | 0.00 |

## 13-blend-color-spaces (1)
| test | framing | base | ab | pyr | mo | moh | ref vs Chromium | self reftest | Chromium self |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| gradient-colorspace-linearrgb-blend | z4 | 100.00 | - | - | 100.00 | 100.00 | 100.00 | 0.00 | 0.00 |

## 14-feoffset-tests (2)
| test | framing | base | ab | pyr | mo | moh | ref vs Chromium | self reftest | Chromium self |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| offset-chained-cancelling | z4 | 33.11 | 33.11 | 33.11 | 33.11 | 33.11 | 0.00 | 0.00 | 33.11 |
| offset-border-stroke-fill | z4 | 7.78 | 7.78 | 7.78 | 1.50 | 1.50 | 0.00 | 38.63 | 37.12 |

## 15-femorphology-tests (3)
| test | framing | base | ab | pyr | mo | moh | ref vs Chromium | self reftest | Chromium self |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| morphology-closing-chain | z4 | 9.95 | 9.95 | 9.95 | 9.95 | 9.95 | 0.00 | 0.00 | 9.95 |
| morphology-erode-horizontal-only | z4 | 11.96 | 11.96 | 11.96 | 0.67 | 0.67 | 0.00 | 0.67 | 0.00 |
| morphology-erode-vertical-only | z4 | 11.54 | 11.54 | 11.54 | 0.50 | 0.50 | 0.00 | 0.50 | 0.00 |

## 16-fegaussianblur-tests (1)
| test | framing | base | ab | pyr | mo | moh | ref vs Chromium | self reftest | Chromium self |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| blur-chained-quadrature | z4 | 2.71 | 2.71 | 2.65 | 2.65 | 2.65 | 0.00 | 0.00 | 2.64 |

## 17-clip-path-tests (47)
| test | framing | base | ab | pyr | mo | moh | ref vs Chromium | self reftest | Chromium self |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clip-path-concentric-circles-evenodd | z4 | 37.95 | 37.95 | 37.95 | 37.95 | 37.95 | 0.21 | 0.73 | 38.01 |
| clip-path-multiple-shapes-union | z2 | 0.66 | 0.66 | 0.66 | 0.66 | 0.66 | 0.12 | 0.68 | 0.00 |
| clip-path-star-evenodd | z2 | 0.61 | 0.61 | 0.61 | 0.61 | 0.61 | 0.00 | 0.62 | 0.00 |
| clip-path-variation-39 | z4 | 0.49 | 0.49 | 0.49 | 0.49 | 0.49 | 0.30 | 0.49 | 0.00 |
| clip-path-ellipse | z4 | 0.48 | 0.48 | 0.48 | 0.48 | 0.48 | 0.22 | 0.48 | 0.00 |
| clip-path-variation-38 | z4 | 0.47 | 0.47 | 0.47 | 0.47 | 0.47 | 0.10 | 0.47 | 0.00 |
| clip-path-variation-33 | z4 | 0.47 | 0.47 | 0.47 | 0.47 | 0.47 | 0.07 | 0.46 | 0.00 |
| clip-path-variation-14 | z4 | 0.44 | 0.44 | 0.44 | 0.44 | 0.44 | 0.12 | 0.43 | 0.00 |
| clip-path-variation-34 | z4 | 0.44 | 0.44 | 0.44 | 0.44 | 0.44 | 0.12 | 0.43 | 0.00 |
| clip-path-polygon-triangle | z4 | 0.43 | 0.43 | 0.43 | 0.43 | 0.43 | 0.00 | 0.43 | 0.00 |
| clip-path-transform-rotate | z4 | 0.43 | 0.43 | 0.43 | 0.43 | 0.43 | 0.00 | 0.43 | 0.00 |
| clip-path-circle | z2 | 0.43 | 0.43 | 0.43 | 0.43 | 0.43 | 0.10 | 0.43 | 0.00 |
| clip-path-variation-28 | z4 | 0.43 | 0.43 | 0.43 | 0.43 | 0.43 | 0.10 | 0.43 | 0.00 |
| clip-path-variation-27 | z4 | 0.43 | 0.43 | 0.43 | 0.43 | 0.43 | 0.29 | 0.42 | 0.00 |
| clip-path-variation-29 | z4 | 0.42 | 0.42 | 0.42 | 0.42 | 0.42 | 0.07 | 0.41 | 0.00 |
| clip-path-variation-22 | z4 | 0.38 | 0.38 | 0.38 | 0.38 | 0.38 | 0.08 | 0.37 | 0.00 |
| clip-path-variation-44 | z4 | 0.36 | 0.36 | 0.36 | 0.36 | 0.36 | 0.09 | 0.37 | 0.00 |
| clip-path-variation-13 | z4 | 0.34 | 0.34 | 0.34 | 0.34 | 0.34 | 0.06 | 0.34 | 0.00 |
| clip-path-variation-19 | z2 | 0.34 | 0.34 | 0.34 | 0.34 | 0.34 | 0.06 | 0.34 | 0.00 |
| clip-path-variation-23 | z2 | 0.34 | 0.34 | 0.34 | 0.34 | 0.34 | 0.06 | 0.34 | 0.00 |
| clip-path-variation-43 | z2 | 0.34 | 0.34 | 0.34 | 0.34 | 0.34 | 0.06 | 0.34 | 0.00 |
| clip-path-variation-47 | z2 | 0.34 | 0.34 | 0.34 | 0.34 | 0.34 | 0.06 | 0.34 | 0.00 |
| clip-path-variation-17 | z4 | 0.34 | 0.34 | 0.34 | 0.34 | 0.34 | 0.05 | 0.34 | 0.00 |
| clip-path-variation-18 | z2 | 0.30 | 0.30 | 0.30 | 0.30 | 0.30 | 0.04 | 0.30 | 0.00 |
| clip-path-variation-42 | z2 | 0.30 | 0.30 | 0.30 | 0.30 | 0.30 | 0.04 | 0.30 | 0.00 |
| clip-path-variation-49 | z4 | 0.30 | 0.30 | 0.30 | 0.30 | 0.30 | 0.07 | 0.29 | 0.00 |
| clip-path-variation-32 | z4 | 0.29 | 0.29 | 0.29 | 0.29 | 0.29 | 0.03 | 0.29 | 0.00 |
| clip-path-variation-26 | z4 | 0.29 | 0.29 | 0.29 | 0.29 | 0.29 | 0.09 | 0.28 | 0.00 |
| clip-path-variation-46 | z4 | 0.29 | 0.29 | 0.29 | 0.29 | 0.29 | 0.09 | 0.28 | 0.00 |
| clip-path-variation-11 | z4 | 0.28 | 0.28 | 0.28 | 0.28 | 0.28 | 0.19 | 0.28 | 0.00 |
| clip-path-variation-31 | z2 | 0.26 | 0.26 | 0.26 | 0.26 | 0.26 | 0.04 | 0.26 | 0.00 |
| clip-path-variation-21 | z2 | 0.26 | 0.26 | 0.26 | 0.26 | 0.26 | 0.04 | 0.26 | 0.00 |
| clip-path-variation-37 | z2 | 0.26 | 0.26 | 0.26 | 0.26 | 0.26 | 0.04 | 0.26 | 0.00 |
| clip-path-variation-41 | z2 | 0.26 | 0.26 | 0.26 | 0.26 | 0.26 | 0.04 | 0.26 | 0.00 |
| clip-path-variation-48 | z4 | 0.26 | 0.26 | 0.26 | 0.26 | 0.26 | 0.06 | 0.26 | 0.00 |
| clip-path-variation-15 | z4 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | 0.17 | 0.25 | 0.00 |
| clip-path-variation-35 | z4 | 0.23 | 0.23 | 0.23 | 0.23 | 0.23 | 0.16 | 0.23 | 0.00 |
| clip-path-variation-12 | z2 | 0.23 | 0.23 | 0.23 | 0.23 | 0.23 | 0.04 | 0.23 | 0.00 |
| clip-path-variation-16 | z2 | 0.23 | 0.23 | 0.23 | 0.23 | 0.23 | 0.04 | 0.23 | 0.00 |
| clip-path-variation-24 | z2 | 0.23 | 0.23 | 0.23 | 0.23 | 0.23 | 0.04 | 0.23 | 0.00 |
| clip-path-variation-36 | z2 | 0.23 | 0.23 | 0.23 | 0.23 | 0.23 | 0.04 | 0.23 | 0.00 |
| clip-path-variation-50 | z4 | 0.20 | 0.20 | 0.20 | 0.20 | 0.20 | 0.07 | 0.20 | 0.00 |
| clip-path-variation-30 | z2 | 0.20 | 0.20 | 0.20 | 0.20 | 0.20 | 0.02 | 0.19 | 0.00 |
| clip-path-variation-25 | z2 | 0.17 | 0.17 | 0.17 | 0.17 | 0.17 | 0.02 | 0.17 | 0.00 |
| clip-path-variation-45 | z2 | 0.17 | 0.17 | 0.17 | 0.17 | 0.17 | 0.02 | 0.17 | 0.00 |
| clip-path-variation-20 | z2 | 0.16 | 0.16 | 0.16 | 0.16 | 0.16 | 0.03 | 0.16 | 0.00 |
| clip-path-variation-40 | z2 | 0.16 | 0.16 | 0.16 | 0.16 | 0.16 | 0.03 | 0.16 | 0.00 |

