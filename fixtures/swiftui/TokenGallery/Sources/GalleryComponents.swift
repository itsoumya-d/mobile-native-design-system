import SwiftUI

struct GalleryCard<Content: View>: View {
    let catalog: TokenCatalog
    @ViewBuilder var content: Content

    var body: some View {
        content
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(catalog.number("component.card.padding"))
            .background(catalog.color("color.surface.default"))
            .clipShape(
                RoundedRectangle(
                    cornerRadius: catalog.number("component.card.radius"),
                    style: .continuous
                )
            )
            .overlay {
                RoundedRectangle(
                    cornerRadius: catalog.number("component.card.radius"),
                    style: .continuous
                )
                .stroke(catalog.color("color.border.subtle"), lineWidth: 1)
            }
    }
}

struct NativePrimaryButtonStyle: ButtonStyle {
    let catalog: TokenCatalog

    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.headline)
            .foregroundStyle(catalog.color("color.action.onPrimary"))
            .frame(maxWidth: .infinity)
            .frame(minHeight: catalog.minimumTouchTarget)
            .padding(.horizontal, catalog.number("component.button.horizontalPadding"))
            .background(catalog.color("color.action.primary"))
            .clipShape(
                RoundedRectangle(
                    cornerRadius: catalog.number("component.button.radius"),
                    style: .continuous
                )
            )
            .opacity(configuration.isPressed ? catalog.number("opacity.pressed") : 1)
            .scaleEffect(configuration.isPressed ? 0.985 : 1)
            .animation(.easeOut(duration: 0.12), value: configuration.isPressed)
    }
}

struct StatusBadge: View {
    let title: String
    let systemImage: String
    let color: Color

    var body: some View {
        Label(title, systemImage: systemImage)
            .font(.caption.weight(.semibold))
            .foregroundStyle(color)
            .padding(.horizontal, 10)
            .padding(.vertical, 6)
            .background(color.opacity(0.12), in: Capsule())
    }
}

struct ScaleHeader: View {
    let title: String
    let detail: String

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title)
                .font(.title3.bold())
            Text(detail)
                .font(.subheadline)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .accessibilityElement(children: .combine)
    }
}
