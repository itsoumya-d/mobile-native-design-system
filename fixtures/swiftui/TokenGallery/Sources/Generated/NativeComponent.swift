// Generated native component contract.
import SwiftUI

enum NativeComponentState {
    case loading
    case empty
    case error
    case populated
}

struct NativeStatusCard: View {
    static let subject = "calm financial wellbeing"
    static let userJob = "Understand one status and take the next safe action."
    static let primaryActionLabel = "Try again"

    let title: String
    let state: NativeComponentState
    let onPrimaryAction: () -> Void

    @ViewBuilder
    private var content: some View {
        switch state {
        case .loading:
            ProgressView().accessibilityLabel("Loading")
        case .empty:
            ContentUnavailableView("Nothing here yet", systemImage: "tray")
        case .error:
            Label("Something went wrong", systemImage: "exclamationmark.triangle")
        case .populated:
            Text(title)
        }
    }

    var body: some View {
        GroupBox {
            VStack(alignment: .leading, spacing: 12) {
                content
                Button(Self.primaryActionLabel, action: onPrimaryAction)
                    .buttonStyle(.borderedProminent)
                    .frame(minHeight: 44)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        }
        .accessibilityElement(children: .contain)
        .accessibilityLabel("\(title), \(String(describing: state))")
    }
}
