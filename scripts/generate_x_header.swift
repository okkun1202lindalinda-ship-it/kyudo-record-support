import AppKit
import Foundation

private struct ScreenPlacement {
  let file: String
  let rect: NSRect
  let angle: CGFloat
}

private enum HeaderError: Error, CustomStringConvertible {
  case imageNotFound(String)
  case pngEncodingFailed(String)

  var description: String {
    switch self {
    case let .imageNotFound(path):
      return "画像を読み込めませんでした: \(path)"
    case let .pngEncodingFailed(path):
      return "PNGを書き出せませんでした: \(path)"
    }
  }
}

@main
private enum HeaderGenerator {
  static func main() throws {
    let rootPath = CommandLine.arguments.dropFirst().first ?? FileManager.default.currentDirectoryPath
    let root = URL(fileURLWithPath: rootPath, isDirectory: true)

    let background = try loadImage(root.appendingPathComponent(
      "assets/images/x-header-background-1500x500.png"
    ))

    let screenFiles = [
      "assets/images/app-record.jpg",
      "assets/images/app-home.jpg",
      "assets/images/app-statistics.jpg",
    ]
    let screens = try screenFiles.map { try loadImage(root.appendingPathComponent($0)) }

    let xHeader = render(
      size: NSSize(width: 1500, height: 500),
      background: background,
      screens: screens,
      placements: [
        ScreenPlacement(
          file: screenFiles[0],
          rect: NSRect(x: 438, y: 46, width: 184, height: 404),
          angle: -6
        ),
        ScreenPlacement(
          file: screenFiles[1],
          rect: NSRect(x: 602, y: 56, width: 184, height: 404),
          angle: 0
        ),
        ScreenPlacement(
          file: screenFiles[2],
          rect: NSRect(x: 766, y: 46, width: 184, height: 404),
          angle: 6
        ),
      ],
      titleRect: NSRect(x: 1004, y: 205, width: 450, height: 190),
      subtitleRect: NSRect(x: 1008, y: 142, width: 420, height: 42),
      titleSize: 46,
      subtitleSize: 24
    )
    try savePNG(
      xHeader,
      to: root.appendingPathComponent("assets/images/x-header-1500x500.png")
    )

    let ogp = render(
      size: NSSize(width: 1200, height: 630),
      background: background,
      screens: screens,
      placements: [
        ScreenPlacement(
          file: screenFiles[0],
          rect: NSRect(x: 88, y: 80, width: 194, height: 426),
          angle: -6
        ),
        ScreenPlacement(
          file: screenFiles[1],
          rect: NSRect(x: 258, y: 100, width: 194, height: 426),
          angle: 0
        ),
        ScreenPlacement(
          file: screenFiles[2],
          rect: NSRect(x: 428, y: 80, width: 194, height: 426),
          angle: 6
        ),
      ],
      titleRect: NSRect(x: 688, y: 260, width: 450, height: 190),
      subtitleRect: NSRect(x: 692, y: 190, width: 420, height: 42),
      titleSize: 48,
      subtitleSize: 25
    )
    try savePNG(ogp, to: root.appendingPathComponent("assets/images/ogp-1200x630.png"))

    print("Generated assets/images/x-header-1500x500.png")
    print("Generated assets/images/ogp-1200x630.png")
  }

  private static func loadImage(_ url: URL) throws -> NSImage {
    guard let image = NSImage(contentsOf: url) else {
      throw HeaderError.imageNotFound(url.path)
    }
    return image
  }

  private static func render(
    size: NSSize,
    background: NSImage,
    screens: [NSImage],
    placements: [ScreenPlacement],
    titleRect: NSRect,
    subtitleRect: NSRect,
    titleSize: CGFloat,
    subtitleSize: CGFloat
  ) -> NSImage {
    let canvas = NSImage(size: size)
    canvas.lockFocus()
    defer { canvas.unlockFocus() }

    background.draw(
      in: NSRect(origin: .zero, size: size),
      from: .zero,
      operation: .copy,
      fraction: 1
    )

    let veil = NSGradient(
      starting: NSColor.white.withAlphaComponent(0.04),
      ending: NSColor.white.withAlphaComponent(0.22)
    )
    veil?.draw(in: NSRect(origin: .zero, size: size), angle: 0)

    for (index, placement) in placements.enumerated() {
      drawPhone(
        screen: screens[index],
        rect: placement.rect,
        angle: placement.angle
      )
    }

    let accentRect = NSRect(
      x: titleRect.minX + 2,
      y: titleRect.maxY + 14,
      width: 74,
      height: 6
    )
    NSColor(calibratedRed: 70 / 255, green: 104 / 255, blue: 155 / 255, alpha: 1)
      .setFill()
    NSBezierPath(roundedRect: accentRect, xRadius: 3, yRadius: 3).fill()

    let paragraph = NSMutableParagraphStyle()
    paragraph.lineSpacing = 8
    paragraph.alignment = .left
    let title = NSAttributedString(
      string: "自分の弓道史を\n共に歩むツール",
      attributes: [
        .font: NSFont.systemFont(ofSize: titleSize, weight: .bold),
        .foregroundColor: NSColor(calibratedWhite: 0.1, alpha: 1),
        .paragraphStyle: paragraph,
        .kern: -1.1,
      ]
    )
    title.draw(
      with: titleRect,
      options: [.usesLineFragmentOrigin, .usesFontLeading]
    )

    let subtitle = NSAttributedString(
      string: "自分だけの弓道ノート",
      attributes: [
        .font: NSFont.systemFont(ofSize: subtitleSize, weight: .semibold),
        .foregroundColor: NSColor(
          calibratedRed: 49 / 255,
          green: 81 / 255,
          blue: 127 / 255,
          alpha: 1
        ),
        .kern: 0.4,
      ]
    )
    subtitle.draw(
      with: subtitleRect,
      options: [.usesLineFragmentOrigin, .usesFontLeading]
    )

    return canvas
  }

  private static func drawPhone(screen: NSImage, rect: NSRect, angle: CGFloat) {
    NSGraphicsContext.saveGraphicsState()
    defer { NSGraphicsContext.restoreGraphicsState() }

    let transform = NSAffineTransform()
    transform.translateX(by: rect.midX, yBy: rect.midY)
    transform.rotate(byDegrees: angle)
    transform.translateX(by: -rect.midX, yBy: -rect.midY)
    transform.concat()

    let shadow = NSShadow()
    shadow.shadowColor = NSColor.black.withAlphaComponent(0.25)
    shadow.shadowBlurRadius = 22
    shadow.shadowOffset = NSSize(width: 0, height: -10)
    shadow.set()

    let framePath = NSBezierPath(roundedRect: rect, xRadius: 28, yRadius: 28)
    NSColor(calibratedWhite: 0.08, alpha: 1).setFill()
    framePath.fill()

    NSGraphicsContext.saveGraphicsState()
    let inner = rect.insetBy(dx: 7, dy: 7)
    NSBezierPath(roundedRect: inner, xRadius: 22, yRadius: 22).addClip()
    screen.draw(
      in: inner,
      from: .zero,
      operation: .sourceOver,
      fraction: 1,
      respectFlipped: true,
      hints: [.interpolation: NSImageInterpolation.high]
    )
    NSGraphicsContext.restoreGraphicsState()
  }

  private static func savePNG(_ image: NSImage, to url: URL) throws {
    guard
      let tiff = image.tiffRepresentation,
      let bitmap = NSBitmapImageRep(data: tiff),
      let png = bitmap.representation(using: .png, properties: [:])
    else {
      throw HeaderError.pngEncodingFailed(url.path)
    }
    try png.write(to: url, options: .atomic)
  }
}
