// Generated native motion contract.
import SwiftUI

enum MobileMotionVariant {
    case rest
    case pressed
    case detail
}

struct MobileMotionModifier: ViewModifier {
    @Environment(\.accessibilityReduceMotion) private var accessibilityReduceMotion
    static let sharedTransitionID = "native-status-card"
    static let totalDuration = 330.0 / 1000.0
    static let interruptionPolicy = "retarget"
    static let restingState = MobileMotionVariant.rest

    func body(content: Content) -> some View {
        content.animation(
            accessibilityReduceMotion ? .easeOut(duration: 0.01) : .easeOut(duration: Self.totalDuration),
            value: accessibilityReduceMotion
        )
    }
}
