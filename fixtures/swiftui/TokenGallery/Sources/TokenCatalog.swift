import Foundation
import SwiftUI

enum GallerySection: String, CaseIterable, Hashable, Identifiable {
    case overview
    case scales
    case components
    case states
    case accessibility

    var id: Self { self }

    var title: String {
        switch self {
        case .overview: "Overview"
        case .scales: "Every scale"
        case .components: "Components"
        case .states: "Async states"
        case .accessibility: "Accessibility"
        }
    }
}

struct TokenCatalog: Sendable {
    static let spacingScale: [Double] = [0, 2, 4, 8, 12, 16, 20, 24, 32, 40, 48, 64]

    let profile: String
    let values: [String: String]

    init(profile: String = "base") {
        self.profile = profile
        self.values = MobileTokens.values(for: profile)
    }

    var minimumTouchTarget: Double {
        number("touchTarget.minimum")
    }

    var allPaths: [String] {
        values.keys.sorted()
    }

    func raw(_ path: String) -> String {
        values[path] ?? ""
    }

    func number(_ path: String) -> Double {
        let rawValue = raw(path)
        if let value = Double(rawValue) {
            return value
        }
        guard
            let data = rawValue.data(using: .utf8),
            let object = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
            let value = object["value"] as? NSNumber
        else {
            return 0
        }
        return value.doubleValue
    }

    func durationMilliseconds(_ path: String) -> Double {
        number(path)
    }

    func color(_ path: String) -> Color {
        Color(hex: raw(path)) ?? .primary
    }

    func paths(prefix: String) -> [(String, String)] {
        values
            .filter { $0.key.hasPrefix(prefix) }
            .sorted { $0.key < $1.key }
    }
}

extension Color {
    init?(hex: String) {
        var cleaned = hex.trimmingCharacters(in: .whitespacesAndNewlines)
        if cleaned.hasPrefix("#") {
            cleaned.removeFirst()
        }
        guard cleaned.count == 6 || cleaned.count == 8,
              let packed = UInt64(cleaned, radix: 16)
        else {
            return nil
        }

        let red: Double
        let green: Double
        let blue: Double
        let alpha: Double
        if cleaned.count == 8 {
            red = Double((packed >> 24) & 0xFF) / 255
            green = Double((packed >> 16) & 0xFF) / 255
            blue = Double((packed >> 8) & 0xFF) / 255
            alpha = Double(packed & 0xFF) / 255
        } else {
            red = Double((packed >> 16) & 0xFF) / 255
            green = Double((packed >> 8) & 0xFF) / 255
            blue = Double(packed & 0xFF) / 255
            alpha = 1
        }
        self.init(.sRGB, red: red, green: green, blue: blue, opacity: alpha)
    }
}
