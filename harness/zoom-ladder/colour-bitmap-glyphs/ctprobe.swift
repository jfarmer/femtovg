// ctprobe SIZE OX OY OUT.png [interp: d|n|l|m|h] [char]
// Draws one emoji with CTFontDrawGlyphs into a white 200x200 sRGB bitmap; origin (OX, OY) in top-down pixel coords.
import CoreText
import CoreGraphics
import Foundation
import ImageIO
import UniformTypeIdentifiers

let a = CommandLine.arguments
let size = CGFloat(Double(a[1])!)
let ox = CGFloat(Double(a[2])!), oy = CGFloat(Double(a[3])!)
let out = a[4]
let interp = a.count > 5 ? a[5] : "d"
let ch = a.count > 6 ? a[6] : "🦀"
let W = 200, H = 200
let cs = CGColorSpace(name: CGColorSpace.sRGB)!
let ctx = CGContext(data: nil, width: W, height: H, bitsPerComponent: 8, bytesPerRow: 0, space: cs,
                    bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
ctx.setFillColor(CGColor(srgbRed: 1, green: 1, blue: 1, alpha: 1))
ctx.fill(CGRect(x: 0, y: 0, width: W, height: H))
switch interp {
case "n": ctx.interpolationQuality = .none
case "l": ctx.interpolationQuality = .low
case "m": ctx.interpolationQuality = .medium
case "h": ctx.interpolationQuality = .high
default: break
}
let font = CTFontCreateWithName("Apple Color Emoji" as CFString, size, nil)
var chars = Array(ch.utf16)
var glyphs = [CGGlyph](repeating: 0, count: chars.count)
CTFontGetGlyphsForCharacters(font, &chars, &glyphs, chars.count)
var rects = [CGRect](repeating: .zero, count: 1)
let bb = CTFontGetBoundingRectsForGlyphs(font, .horizontal, glyphs, &rects, 1)
var adv = CGSize.zero
CTFontGetAdvancesForGlyphs(font, .horizontal, glyphs, &adv, 1)
var opt = [CGRect](repeating: .zero, count: 1)
CTFontGetOpticalBoundsForGlyphs(font, glyphs, &opt, 1, 0)
FileHandle.standardError.write("size \(size) glyph \(glyphs[0]) bounds \(rects[0]) optical \(opt[0]) adv \(adv.width) ascent \(CTFontGetAscent(font)) descent \(CTFontGetDescent(font)) leading \(CTFontGetLeading(font)) interp \(ctx.interpolationQuality.rawValue)\n".data(using: .utf8)!)
var pos = [CGPoint(x: ox, y: CGFloat(H) - oy)]
CTFontDrawGlyphs(font, glyphs, &pos, 1, ctx)
let img = ctx.makeImage()!
let dest = CGImageDestinationCreateWithURL(URL(fileURLWithPath: out) as CFURL, UTType.png.identifier as CFString, 1, nil)!
CGImageDestinationAddImage(dest, img, nil)
CGImageDestinationFinalize(dest)
