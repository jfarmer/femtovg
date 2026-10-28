# linebender/resvg#1166 (text-path arc length): counters on A14 / A12 E-cores

Question: the PR author reports that their second commit (2acf581, `CurveWithLength` caches the segment length)
made parse + layout of a 1,000-glyph straight text path ~3 % slower than unoptimised `0.001`. What do the counters say,
and what change would help on every core?

## What was measured

`bench/src/lib.rs` is `collect_normals`' hot loop (usvg `crates/usvg/src/text/layout.rs`) on kurbo 0.13.1 (resvg's lock),
glyph advance 9 units, offsets ascending, 9 workloads = {100, 500, 1000} glyphs x {straight (usvg's LineTo cubic with
control points at 0.33/0.66), one S cubic, 32 cubics}. Variants: `plain0.5` (master), `plain0.001` (PR), `cached0.001`
(2acf581, verbatim), `incr0.001` (candidate, `usvg/suggested-resume.patch`). `app/` is a tiny iOS app that runs it on a
background-QoS thread (E-cores); `thread_selfcounts` gives exact instructions/cycles per call, xctrace "CPU Counters"
(manual event sets, 1 ms time sampling, `rec.sh`) gives the events per signpost interval. iPhone 12 (A14, iOS 26.5) and
iPhone XS Max (A12). The iPhone SE (A13) was locked and was not run.

## A14 E-cores: per call (one call = the whole glyph run), 20 rounds x 10 calls, medians

```
workload       variant        instr/call     cyc/call   IPC P-core% vs plain0.001 instr     cyc  cyc spread
straight-100   plain0.5           265392       173857  1.53     0.0             -21.9%  -22.9%  173336..178411
straight-100   plain0.001         339754       225421  1.51     0.0              +0.0%   +0.0%  224694..232090
straight-100   cached0.001        312138       207316  1.51     0.0              -8.1%   -8.0%  206866..210636
straight-100   incr0.001          102381        56599  1.81     0.0             -69.9%  -74.9%  56348..58919
straight-500   plain0.5          1444676       947814  1.52     0.0             -16.4%  -17.2%  944118..955977
straight-500   plain0.001        1728510      1145299  1.51     0.0              +0.0%   +0.0%  1140815..1159777
straight-500   cached0.001       1591080      1055174  1.51     0.0              -8.0%   -7.9%  1050910..1075737
straight-500   incr0.001          426884       233102  1.83     0.0             -75.3%  -79.6%  232448..241280
straight-1000  plain0.5          2970396      1948867  1.52     0.0             -14.6%  -15.2%  1942718..1990061
straight-1000  plain0.001        3478427      2297958  1.51     0.0              +0.0%   +0.0%  2294408..2326966
straight-1000  cached0.001       3204091      2122036  1.51     0.0              -7.9%   -7.7%  2114212..2164340
straight-1000  incr0.001          644882       344737  1.87     0.0             -81.5%  -85.0%  343305..351064
cubic-100      plain0.5           282217       188967  1.49     0.0             -22.2%  -22.3%  187922..192988
cubic-100      plain0.001         362592       243316  1.49     0.0              +0.0%   +0.0%  242570..256785
cubic-100      cached0.001        319512       215583  1.48     0.0             -11.9%  -11.4%  214613..222679
cubic-100      incr0.001          116542        69947  1.67     0.0             -67.9%  -71.3%  69119..72811
cubic-500      plain0.5          1569841      1044454  1.50     0.0             -17.0%  -17.2%  1041664..1061182
cubic-500      plain0.001        1891124      1261722  1.50     0.0              +0.0%   +0.0%  1257329..1280989
cubic-500      cached0.001       1674726      1121594  1.49     0.0             -11.4%  -11.1%  1118862..1130810
cubic-500      incr0.001          578018       341408  1.69     0.0             -69.4%  -72.9%  339315..346189
cubic-1000     plain0.5          3194140      2123984  1.50     0.0             -16.4%  -16.6%  2115892..2152979
cubic-1000     plain0.001        3820987      2548175  1.50     0.0              +0.0%   +0.0%  2538844..2575595
cubic-1000     cached0.001       3389533      2271290  1.49     0.0             -11.3%  -10.9%  2260331..2302738
cubic-1000     incr0.001         1149275       674263  1.70     0.0             -69.9%  -73.5%  672663..686525
multi-100      plain0.5           231189       149062  1.55     0.0             -29.2%  -31.2%  148088..153891
multi-100      plain0.001         326499       216813  1.51     0.0              +0.0%   +0.0%  215629..222844
multi-100      cached0.001        298775       198768  1.50     0.0              -8.5%   -8.3%  197394..208270
multi-100      incr0.001          177567       107586  1.65     0.0             -45.6%  -50.4%  106725..111248
multi-500      plain0.5          1282783       834000  1.54     0.0             -23.5%  -25.1%  830743..876847
multi-500      plain0.001        1676175      1113965  1.50     0.0              +0.0%   +0.0%  1110411..1149105
multi-500      cached0.001       1537841      1020069  1.51     0.0              -8.3%   -8.4%  1017332..1057556
multi-500      incr0.001          635838       372710  1.71     0.0             -62.1%  -66.5%  370070..388390
multi-1000     plain0.5          2667858      1738729  1.53     0.0             -21.7%  -23.3%  1733340..1768765
multi-1000     plain0.001        3409378      2266939  1.50     0.0              +0.0%   +0.0%  2257983..2306559
multi-1000     cached0.001       3133072      2079084  1.51     0.0              -8.1%   -8.3%  2073610..2117959
multi-1000     incr0.001         1257446       727602  1.73     0.0             -63.1%  -67.9%  724764..743228
```

`cached0.001` is -8 % instructions and -8 % cycles in all nine shapes (-11..-12 % on the one-cubic shapes), never slower.
On the A12 (IPC 0.5 there) the same variant saves more cycles than instructions (-10..-17 %): the call it removes is
sqrt/divide-heavy.

## A12 E-cores, same run

```
workload       variant        instr/call     cyc/call   IPC P-core% vs plain0.001 instr     cyc  cyc spread
straight-100   plain0.5           266834       493275  0.54     0.0             -22.1%  -23.5%  490826..506772
straight-100   plain0.001         342618       644708  0.53     0.0              +0.0%   +0.0%  636229..678688
straight-100   cached0.001        314348       576877  0.54     0.0              -8.3%  -10.5%  569865..589959
straight-100   incr0.001          102710       167570  0.61     0.0             -70.0%  -74.0%  166070..184259
straight-500   plain0.5          1454535      2705629  0.54     0.0             -16.4%  -17.1%  2683009..2779010
straight-500   plain0.001        1739488      3263068  0.53     0.0              +0.0%   +0.0%  3233977..3353726
straight-500   cached0.001       1601581      2932524  0.55     0.0              -7.9%  -10.1%  2913016..2984909
straight-500   incr0.001          428540       678389  0.63     0.0             -75.4%  -79.2%  672909..700540
straight-1000  plain0.5          2991377      5567592  0.54     0.0             -14.6%  -15.3%  5546214..5752154
straight-1000  plain0.001        3504267      6571811  0.53     0.0              +0.0%   +0.0%  6539911..6825853
straight-1000  cached0.001       3223839      5899333  0.55     0.0              -8.0%  -10.2%  5865338..6048189
straight-1000  incr0.001          648223       963227  0.67     0.0             -81.5%  -85.3%  955737..1008425
cubic-100      plain0.5           284417       543100  0.52     0.0             -22.3%  -24.9%  536399..558223
cubic-100      plain0.001         365919       723198  0.51     0.0              +0.0%   +0.0%  713834..755450
cubic-100      cached0.001        321444       600792  0.54     0.0             -12.2%  -16.9%  595376..616861
cubic-100      incr0.001          117095       197554  0.59     0.0             -68.0%  -72.7%  196665..202351
cubic-500      plain0.5          1580783      3010883  0.53     0.0             -17.0%  -19.7%  2998540..3066938
cubic-500      plain0.001        1905301      3750991  0.51     0.0              +0.0%   +0.0%  3727728..3788380
cubic-500      cached0.001       1684725      3140900  0.54     0.0             -11.6%  -16.3%  3123085..3229500
cubic-500      incr0.001          581790       978226  0.59     0.0             -69.5%  -73.9%  970717..992581
cubic-1000     plain0.5          3216562      6131712  0.52     0.0             -16.5%  -19.1%  6097275..6208279
cubic-1000     plain0.001        3851438      7578975  0.51     0.0              +0.0%   +0.0%  7537552..7669536
cubic-1000     cached0.001       3414613      6370983  0.54     0.0             -11.3%  -15.9%  6340257..6512067
cubic-1000     incr0.001         1156244      1946806  0.59     0.0             -70.0%  -74.3%  1931444..2007489
multi-100      plain0.5           232768       417646  0.56     0.0             -29.1%  -31.5%  413268..445815
multi-100      plain0.001         328250       609421  0.54     0.0              +0.0%   +0.0%  602744..649646
multi-100      cached0.001        300804       539746  0.56     0.0              -8.4%  -11.4%  535478..558775
multi-100      incr0.001          178815       309985  0.58     0.0             -45.5%  -49.1%  304992..336906
multi-500      plain0.5          1290460      2334689  0.55     0.0             -23.6%  -25.2%  2316298..2428732
multi-500      plain0.001        1688037      3119521  0.54     0.0              +0.0%   +0.0%  3099726..3235213
multi-500      cached0.001       1546594      2783118  0.56     0.0              -8.4%  -10.8%  2768162..2887244
multi-500      incr0.001          639769      1046544  0.61     0.0             -62.1%  -66.5%  1034934..1065129
multi-1000     plain0.5          2683320      4869076  0.55     0.0             -21.7%  -23.2%  4848318..4921206
multi-1000     plain0.001        3427973      6336497  0.54     0.0              +0.0%   +0.0%  6311847..6487398
multi-1000     cached0.001       3158256      5689795  0.56     0.0              -7.9%  -10.2%  5646439..5750315
multi-1000     incr0.001         1264776      2049394  0.62     0.0             -63.1%  -67.7%  2026919..2085475
```

## Why: events per 1000 instructions (A14 E-cores, sampled; intervals after the first)

```
set3 straight-1000: events per 1000 instructions (E-cores, sampled; warm intervals)
variant      intervals  instr M   IPC       LDST     BRANCH BR_MISPRED L1D_MISS_LD L1D_MISS_ST L1D_TLB_MISS L2_TLB_MISS YMAP_STALL
plain0.5             5    292.5  1.53      98.26      31.78       0.09       0.02       0.00       0.01       0.00     382.62
plain0.001           5    345.0  1.52      96.87      30.30       0.07       0.02       0.00       0.01       0.00     389.23
cached0.001          5    318.5  1.51     101.27      32.52       0.08       0.02       0.00       0.01       0.00     389.37
incr0.001            5     64.5  1.85      95.58      66.48       0.04       0.05       0.02       0.02       0.00     270.42

set3 multi-1000: events per 1000 instructions (E-cores, sampled; warm intervals)
variant      intervals  instr M   IPC       LDST     BRANCH BR_MISPRED L1D_MISS_LD L1D_MISS_ST L1D_TLB_MISS L2_TLB_MISS YMAP_STALL
plain0.5             5    267.6  1.54     102.52      42.02       0.42       0.04       0.00       0.00       0.00     370.27
plain0.001           5    337.4  1.51      99.57      37.48       0.51       0.05       0.00       0.01       0.00     382.59
cached0.001          5    310.8  1.51     104.34      40.47       0.49       0.04       0.00       0.01       0.00     381.73
incr0.001            5    125.2  1.72      95.43      74.67       0.38       0.05       0.01       0.01       0.00     304.71

set2b straight-1000: events per 1000 instructions (E-cores, sampled; warm intervals)
variant      intervals  instr M   IPC    INT_ALU L1D_MISS_LD L1D_MISS_ST MAP_DISPATCH_BUBBLE   L1I_MISS ZMAP_REWIND L2_TLB_MISS_I     L1D_WB
plain0.5             5    294.7  1.53     104.41       0.02       0.00       0.29       0.01       0.65       0.00       0.03
plain0.001           5    347.7  1.52     102.12       0.02       0.00       0.25       0.01       0.47       0.00       0.03
cached0.001          5    319.3  1.51     101.60       0.02       0.00       0.35       0.01       0.50       0.00       0.03
incr0.001            5     63.9  1.86     118.30       0.04       0.01       0.46       0.02       0.11       0.01       0.04

set2b multi-1000: events per 1000 instructions (E-cores, sampled; warm intervals)
variant      intervals  instr M   IPC    INT_ALU L1D_MISS_LD L1D_MISS_ST MAP_DISPATCH_BUBBLE   L1I_MISS ZMAP_REWIND L2_TLB_MISS_I     L1D_WB
plain0.5             5    268.6  1.54     109.20       0.04       0.00       0.31       0.01       3.26       0.00       0.03
plain0.001           5    335.0  1.51     104.78       0.03       0.00       0.35       0.01       3.62       0.00       0.02
cached0.001          5    304.4  1.51     104.49       0.04       0.00       0.41       0.01       3.81       0.00       0.03
incr0.001            5    125.5  1.72     123.50       0.05       0.01       1.14       0.02       2.82       0.01       0.03

set1 straight-1000: events per 1000 instructions (E-cores, sampled; warm intervals)
variant      intervals  instr M   IPC   SIMD_ALU    SIMD_LD    SIMD_ST L1D_MISS_LD L1D_MISS_ST     L1D_WB L1D_TLB_MISS YMAP_STALL
plain0.5             5    294.2  1.53     751.73      63.49      17.48       0.02       0.00       0.03       0.01     382.08
plain0.001           5    350.0  1.52     756.85      63.31      17.37       0.02       0.00       0.03       0.00     388.75
cached0.001          5    318.1  1.52     750.35      64.07      17.93       0.02       0.00       0.04       0.01     389.43
incr0.001            5     61.9  1.84     705.44      65.72      18.35       0.06       0.02       0.05       0.03     270.71

set1 multi-1000: events per 1000 instructions (E-cores, sampled; warm intervals)
variant      intervals  instr M   IPC   SIMD_ALU    SIMD_LD    SIMD_ST L1D_MISS_LD L1D_MISS_ST     L1D_WB L1D_TLB_MISS YMAP_STALL
plain0.5             5    265.9  1.54     732.70      68.24      16.71       0.04       0.00       0.03       0.00     370.50
plain0.001           5    333.0  1.51     744.39      66.93      16.73       0.06       0.00       0.04       0.01     382.54
cached0.001          5    309.8  1.51     736.54      68.02      17.25       0.05       0.00       0.04       0.01     381.39
incr0.001            5    123.7  1.73     693.20      71.23      14.37       0.05       0.01       0.02       0.01     304.38

```

Branch mispredicts are 0.07 per 1000 instructions on the straight path (0.2 per glyph; at the worst shape, 32 cubics,
0.5 per 1000 = 1,700 per call = ~1 % of cycles if each costs ~15 cycles), L1D/L1I/TLB misses are ~0.0x per 1000: the kernel lives in registers and 64 bytes of curve.
It is a floating-point dependency chain: ~76 % of instructions are SIMD/FP ALU ops (scalar `hypot`/`sqrt`/divide),
IPC 1.5, and the map-stage stall counter is 0.39 per instruction (~60 % of cycles). The three non-`incr` variants have
the same rates; they differ only in how many `arclen` evaluations a glyph needs (counted: 7.9 per glyph for
`inv_arclen`, 6.9 when the total length is cached, `bench/examples/check2.rs`).

Nothing in the counters moves for `cached0.001` except the call count, so the kernel cannot be what made parse + layout
3 % slower.

## Whole parse + layout (usvg::Tree::from_str, M4 Max E-cores, `usvg/arc_e2e.rs`, `results/mac/usvg-e2e.txt`)

1,000-glyph straight path: 59.9 M instructions for the whole `from_str`, of which the kernel is ~3.5 M (~6 %).
plain0.5 -> plain0.001 is +0.8 % of the total; `cached0.001` is -0.5 % instructions / -0.9 % cycles (inside the
26.0-33.2 M-cycle spread of one variant); `resume0.001` is -4.8 % instructions / -3.5 % cycles. The kernel is too small a
share for a 3 % change in this metric to come from it; the run-to-run spread of `from_str` cycles is 15-28 %
(min to max of 30 runs).

## The candidate: resume from the previous glyph (`usvg/suggested-resume.patch`, 62 lines on 3826dce)

`kurbo::inv_arclen` measures `arclen(0..t)` from t = 0 for every probe (7.9 `arclen` calls per glyph, each an error
estimate over 8 points, with a divide each, plus a quadrature with a `hypot` per point). Glyph offsets ascend, so the previous glyph's (t, arc length) is a bracket start:
Newton on the arc length of the short piece, speed `|B'(t)|` as derivative, falls back to `inv_arclen` when the target is
behind, the speed vanishes or six steps do not converge; the running arc length is re-measured from the start every 16
glyphs so the piece errors cannot add up.

* kernel, A14 E-cores: -68..-82 % instructions and -71..-85 % cycles on the straight and one-cubic shapes (-46..-63 %
  and -50..-69 % on 32 cubics); A12: the same within a few points. IPC goes up (1.5 -> 1.85) and mispredicts per instruction do not (0.04 vs 0.07).
* accuracy against kurbo at 1e-9 (position): plain0.5 max 0.39-0.65, plain0.001 max 0.0012, resume max 0.0008 (9 workloads);
* 43 text-path fixtures (671 glyphs): worst resume-vs-plain0.001 glyph position 0.00102, matrices equal to 1e-6;
* `cargo test -p usvg` passes (including `text_path_start_offset_is_accurate`), `cargo fmt --check` clean, no new clippy warning;
* not run: resvg's PNG reftests (the fixture PNGs were not checked out); the glyph transforms above are what they render from.

## Reproduce

`cd bench && IPHONEOS_DEPLOYMENT_TARGET=16.0 cargo build --release --lib --target aarch64-apple-ios`, copy
`libarclen_bench.a` to `app/lib/`, `xcodegen`, build, install, `DEVICECTL_CHILD_ARC_*` env (see `app/Sources/Main.swift`),
`python3 bench/summarize.py out.csv`; `rec.sh set3|set2b|set1 tag kinds "" rounds inner` for the events
(set2 is rejected on the A14: conflicting INST_INT_ST; use set2b). `usvg/instrumented-variants.diff` + `arc_e2e.rs` /
`fixtures_cmp.rs` are the run-time variant switch and the two usvg examples (resvg PR branch at 2acf581).
