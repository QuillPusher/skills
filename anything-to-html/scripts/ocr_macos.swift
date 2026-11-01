// OCR one or more images with Apple's Vision framework (macOS 10.15+).
// Needs only the Xcode Command Line Tools for the `swift` command
// (`xcode-select --install`); no Python packages, no Tesseract.
//
//   swift ocr_macos.swift page1.png [page2.png ...]
//
// Prints the recognised text for each file, separated by a line "===== <file>".
// Lines that are clearly further apart than normal line spacing get a blank
// line between them, so paragraphs survive. Called by extract_pdf.py --ocr macos.
import Foundation
import AppKit
import Vision

let files = Array(CommandLine.arguments.dropFirst())
if files.isEmpty {
    FileHandle.standardError.write("usage: swift ocr_macos.swift IMAGE [IMAGE ...]\n".data(using: .utf8)!)
    exit(2)
}

struct Line {
    let text: String
    let top: CGFloat
    let bottom: CGFloat
    let left: CGFloat
    var height: CGFloat { bottom - top }
}

for path in files {
    print("===== \(path)")
    guard let image = NSImage(contentsOfFile: path),
          let cg = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
        FileHandle.standardError.write("cannot read image: \(path)\n".data(using: .utf8)!)
        continue
    }
    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = true
    let handler = VNImageRequestHandler(cgImage: cg, options: [:])
    do {
        try handler.perform([request])
    } catch {
        FileHandle.standardError.write("OCR failed for \(path): \(error)\n".data(using: .utf8)!)
        continue
    }
    let observations = (request.results as? [VNRecognizedTextObservation]) ?? []

    // Vision's boundingBox is normalised with the origin at the bottom left;
    // flip it so lines sort top to bottom, then left to right.
    var lines: [Line] = []
    for o in observations {
        guard let best = o.topCandidates(1).first else { continue }
        lines.append(Line(text: best.string, top: 1 - o.boundingBox.maxY, bottom: 1 - o.boundingBox.minY, left: o.boundingBox.minX))
    }
    lines.sort { $0.top != $1.top ? $0.top < $1.top : $0.left < $1.left }

    let heights = lines.map { $0.height }.sorted()
    let typical = heights.isEmpty ? 0 : heights[heights.count / 2]
    var previousBottom: CGFloat? = nil
    for line in lines {
        if let pb = previousBottom, line.top - pb > 0.9 * typical { print("") }
        print(line.text)
        previousBottom = line.bottom
    }
}
