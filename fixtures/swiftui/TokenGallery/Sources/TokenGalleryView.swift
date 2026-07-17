import SwiftUI

private enum GallerySheet: String, Identifiable {
    case tokenDetails
    var id: String { rawValue }
}

private enum GalleryDataState: String, CaseIterable, Identifiable {
    case loading
    case empty
    case error
    case populated
    var id: String { rawValue }
}

struct TokenGalleryView: View {
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @Environment(\.colorScheme) private var colorScheme
    @Environment(\.colorSchemeContrast) private var contrast
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass

    @State private var dataState: GalleryDataState = .populated
    @State private var sheet: GallerySheet?
    @State private var showInsight = true
    @State private var name = "Avery"
    @State private var notificationsEnabled = true

    private var profile: String {
        if contrast == .increased { return "highContrast" }
        return colorScheme == .dark ? "dark" : "light"
    }

    private var catalog: TokenCatalog { TokenCatalog(profile: profile) }
    private var gridColumns: [GridItem] {
        [GridItem(.adaptive(minimum: horizontalSizeClass == .regular ? 260 : 152), spacing: 16)]
    }

    var body: some View {
        NavigationStack {
            ScrollView {
                LazyVStack(alignment: .leading, spacing: 32) {
                    overview
                    everyScale
                    components
                    states
                    accessibilityStress
                }
                .padding(.horizontal, catalog.number("layout.margin.compact"))
                .padding(.vertical, 24)
            }
            .background(catalog.color("color.surface.canvas"))
            .navigationTitle("Token Gallery")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button {
                        sheet = .tokenDetails
                    } label: {
                        Image(systemName: "info.circle")
                    }
                    .accessibilityLabel("About the token contract")
                }
            }
            .sheet(item: $sheet) { _ in
                TokenDetailSheet(catalog: catalog)
            }
        }
        .tint(catalog.color("color.action.primary"))
    }

    private var overview: some View {
        VStack(alignment: .leading, spacing: 16) {
            ScaleHeader(
                title: GallerySection.overview.title,
                detail: "A financial-wellbeing subject, one semantic contract, native behavior."
            )
            LazyVGrid(columns: gridColumns, spacing: 16) {
                scoreCard
                GalleryCard(catalog: catalog) {
                    VStack(alignment: .leading, spacing: 12) {
                        Label("Contract health", systemImage: "checkmark.seal.fill")
                            .font(.headline)
                        Text("\(catalog.allPaths.count) semantic tokens")
                            .font(.title2.bold())
                        Text("Light, dark, high contrast, Apple, Android, and reduced-motion resolvers.")
                            .foregroundStyle(.secondary)
                    }
                }
            }
        }
        .accessibilityIdentifier("gallery-overview")
    }

    private var scoreCard: some View {
        GalleryCard(catalog: catalog) {
            HStack(spacing: 20) {
                ZStack {
                    Circle()
                        .stroke(catalog.color("color.border.subtle"), lineWidth: 10)
                    Circle()
                        .trim(from: 0, to: 0.72)
                        .stroke(
                            catalog.color("color.status.positive"),
                            style: StrokeStyle(lineWidth: 10, lineCap: .round)
                        )
                        .rotationEffect(.degrees(-90))
                    Text("72")
                        .font(.title.bold())
                }
                .frame(width: 104, height: 104)
                .accessibilityHidden(true)

                VStack(alignment: .leading, spacing: 8) {
                    StatusBadge(
                        title: "Improving",
                        systemImage: "arrow.up.right",
                        color: catalog.color("color.status.positive")
                    )
                    Text("Wellbeing score")
                        .font(.headline)
                    Text("Up 4 points. Your emergency fund is the next best action.")
                        .foregroundStyle(.secondary)
                }
            }
            .accessibilityElement(children: .combine)
            .accessibilityLabel("Financial wellbeing score")
            .accessibilityValue("72 out of 100, improving, up 4 points")
        }
    }

    private var everyScale: some View {
        VStack(alignment: .leading, spacing: 20) {
            ScaleHeader(
                title: GallerySection.scales.title,
                detail: "Color, opacity, type, spacing, size, icons, targets, shape, elevation, layout, layers, motion, haptics, and states."
            )
            colorScale
            typographyScale
            spacingScale
            compactTokenGroups
        }
        .accessibilityIdentifier("gallery-scales")
    }

    private var colorScale: some View {
        GalleryCard(catalog: catalog) {
            Text("Semantic color")
                .font(.headline)
            LazyVGrid(columns: gridColumns, spacing: 12) {
                ForEach(catalog.paths(prefix: "color."), id: \.0) { path, _ in
                    HStack {
                        RoundedRectangle(cornerRadius: 8, style: .continuous)
                            .fill(catalog.color(path))
                            .frame(width: 44, height: 44)
                            .overlay {
                                RoundedRectangle(cornerRadius: 8)
                                    .stroke(.primary.opacity(0.12))
                            }
                        Text(path.replacingOccurrences(of: "color.", with: ""))
                            .font(.caption)
                            .lineLimit(2)
                        Spacer()
                    }
                    .accessibilityElement(children: .combine)
                }
            }
        }
    }

    private var typographyScale: some View {
        GalleryCard(catalog: catalog) {
            Text("Semantic typography")
                .font(.headline)
            Group {
                Text("Large title · Progress with purpose").font(.largeTitle.bold())
                Text("Title · Monthly outlook").font(.title.bold())
                Text("Headline · Savings momentum").font(.headline)
                Text("Body · Build a buffer without losing sight of today's needs.").font(.body)
                Text("Label · VIEW PLAN").font(.subheadline.weight(.semibold))
                Text("Caption · Updated two minutes ago").font(.caption)
            }
            .fixedSize(horizontal: false, vertical: true)
        }
    }

    private var spacingScale: some View {
        GalleryCard(catalog: catalog) {
            Text("Spacing · logical units")
                .font(.headline)
            ForEach(TokenCatalog.spacingScale, id: \.self) { value in
                HStack {
                    Text(value.formatted())
                        .font(.caption.monospacedDigit())
                        .frame(width: 32, alignment: .trailing)
                    RoundedRectangle(cornerRadius: 3)
                        .fill(catalog.color("color.action.primary"))
                        .frame(width: max(2, value * 3), height: 8)
                    Spacer()
                }
            }
        }
    }

    private var compactTokenGroups: some View {
        LazyVGrid(columns: gridColumns, spacing: 16) {
            ForEach(
                [
                    ("Sizing", "sizing."),
                    ("Iconography", "iconography."),
                    ("Touch targets", "touchTarget."),
                    ("Radii", "radius."),
                    ("Strokes", "stroke."),
                    ("Elevation", "elevation."),
                    ("Layout", "layout."),
                    ("Layers", "zIndex."),
                    ("Motion", "motion."),
                    ("Haptics", "haptic."),
                    ("Opacity", "opacity."),
                    ("Component state", "component.")
                ],
                id: \.0
            ) { title, prefix in
                GalleryCard(catalog: catalog) {
                    Text(title).font(.headline)
                    ForEach(catalog.paths(prefix: prefix).prefix(8), id: \.0) { path, value in
                        HStack(alignment: .firstTextBaseline) {
                            Text(path.replacingOccurrences(of: prefix, with: ""))
                                .lineLimit(2)
                            Spacer()
                            Text(value)
                                .foregroundStyle(.secondary)
                                .lineLimit(1)
                        }
                        .font(.caption)
                    }
                    if catalog.paths(prefix: prefix).count > 8 {
                        Text("+\(catalog.paths(prefix: prefix).count - 8) more")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                }
            }
        }
    }

    private var components: some View {
        VStack(alignment: .leading, spacing: 16) {
            ScaleHeader(
                title: GallerySection.components.title,
                detail: "System controls retain semantics, scaling, focus, and touch geometry."
            )
            GalleryCard(catalog: catalog) {
                Button("Build my buffer") {}
                    .buttonStyle(NativePrimaryButtonStyle(catalog: TokenCatalog(profile: "ios")))
                    .accessibilityHint("Opens a savings plan")

                HStack {
                    Button("Secondary action") {}
                        .buttonStyle(.bordered)
                        .controlSize(.large)
                    Spacer()
                    Button {} label: {
                        Image(systemName: "slider.horizontal.3")
                            .frame(
                                width: TokenCatalog(profile: "ios").minimumTouchTarget,
                                height: TokenCatalog(profile: "ios").minimumTouchTarget
                            )
                    }
                    .buttonStyle(.bordered)
                    .accessibilityLabel("Adjust dashboard")
                }

                TextField("Preferred name", text: $name)
                    .textFieldStyle(.roundedBorder)
                    .accessibilityLabel("Preferred name")

                Toggle("Weekly progress notifications", isOn: $notificationsEnabled)

                NavigationLink {
                    TokenListView(catalog: catalog)
                } label: {
                    Label("Browse all semantic paths", systemImage: "list.bullet.rectangle")
                        .frame(minHeight: TokenCatalog(profile: "ios").minimumTouchTarget)
                }

                Button("Present native sheet") {
                    sheet = .tokenDetails
                }
            }

            GalleryCard(catalog: catalog) {
                Button {
                    if reduceMotion {
                        showInsight.toggle()
                    } else {
                        withAnimation(.spring(response: 0.36, dampingFraction: 0.84)) {
                            showInsight.toggle()
                        }
                    }
                } label: {
                    Label(showInsight ? "Hide insight" : "Show insight", systemImage: "sparkles")
                }
                .frame(minHeight: TokenCatalog(profile: "ios").minimumTouchTarget)

                if showInsight {
                    Label(
                        "Saving ₹2,000 more this month reaches 3 months of runway.",
                        systemImage: "leaf.fill"
                    )
                    .padding()
                    .background(catalog.color("color.surface.selected"), in: RoundedRectangle(cornerRadius: 12))
                    .transition(reduceMotion ? .opacity : .move(edge: .top).combined(with: .opacity))
                }
            }
        }
        .accessibilityIdentifier("gallery-components")
    }

    private var states: some View {
        VStack(alignment: .leading, spacing: 16) {
            ScaleHeader(
                title: GallerySection.states.title,
                detail: "Loading, empty, error, recovery, and populated content use stable native layouts."
            )
            Picker("Data state", selection: $dataState) {
                ForEach(GalleryDataState.allCases) { state in
                    Text(state.rawValue.capitalized).tag(state)
                }
            }
            .pickerStyle(.segmented)

            GalleryCard(catalog: catalog) {
                switch dataState {
                case .loading:
                    ForEach(0..<3, id: \.self) { index in
                        Label("Account \(index + 1)", systemImage: "creditcard")
                            .frame(maxWidth: .infinity, minHeight: 56, alignment: .leading)
                    }
                    .redacted(reason: .placeholder)
                    .accessibilityLabel("Loading accounts")
                case .empty:
                    ContentUnavailableView(
                        "No goals yet",
                        systemImage: "target",
                        description: Text("Create a goal to turn a plan into progress.")
                    )
                case .error:
                    ContentUnavailableView {
                        Label("Couldn't refresh", systemImage: "exclamationmark.triangle")
                    } description: {
                        Text("Your last saved snapshot is still available.")
                    } actions: {
                        Button("Try again") { dataState = .loading }
                    }
                case .populated:
                    ForEach(
                        [
                            ("Emergency fund", "₹84,000", "2.8 months"),
                            ("Travel goal", "₹36,500", "61 percent"),
                            ("Credit balance", "₹18,200", "down 12 percent")
                        ],
                        id: \.0
                    ) { title, value, detail in
                        HStack {
                            VStack(alignment: .leading) {
                                Text(title).font(.headline)
                                Text(detail).foregroundStyle(.secondary)
                            }
                            Spacer()
                            Text(value).font(.headline.monospacedDigit())
                        }
                        .frame(minHeight: 56)
                        .accessibilityElement(children: .combine)
                    }
                }
            }
        }
        .accessibilityIdentifier("gallery-states")
    }

    private var accessibilityStress: some View {
        VStack(alignment: .leading, spacing: 16) {
            ScaleHeader(
                title: GallerySection.accessibility.title,
                detail: "Large text, mixed direction, non-color status, targets, and reduced motion."
            )
            GalleryCard(catalog: catalog) {
                Text("Your emergency fund could cover two months, three weeks, and four days of essential expenses.")
                    .font(.title3.bold())
                    .fixedSize(horizontal: false, vertical: true)

                HStack(alignment: .firstTextBaseline) {
                    Label("On track", systemImage: "checkmark.circle.fill")
                        .foregroundStyle(catalog.color("color.status.positive"))
                    Spacer()
                    Text("+12%")
                        .font(.headline.monospacedDigit())
                }
                .accessibilityElement(children: .combine)
                .accessibilityLabel("Savings status, on track, up 12 percent")

                HStack {
                    Text("الادخار الشهري")
                    Spacer()
                    Text("₹١٢٬٥٠٠")
                        .monospacedDigit()
                }
                .environment(\.layoutDirection, .rightToLeft)
                .accessibilityElement(children: .combine)
                .accessibilityLabel("Monthly savings, 12,500 rupees")

                Label(
                    reduceMotion ? "Reduced motion is active" : "Standard motion is active",
                    systemImage: reduceMotion ? "figure.walk.motion" : "sparkles"
                )
                .foregroundStyle(.secondary)
            }
        }
        .accessibilityIdentifier("gallery-accessibility")
    }
}

private struct TokenListView: View {
    let catalog: TokenCatalog

    var body: some View {
        List(catalog.allPaths, id: \.self) { path in
            VStack(alignment: .leading) {
                Text(path).font(.body.monospaced())
                Text(catalog.raw(path))
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
        }
        .navigationTitle("Semantic paths")
    }
}

private struct TokenDetailSheet: View {
    @Environment(\.dismiss) private var dismiss
    let catalog: TokenCatalog

    var body: some View {
        NavigationStack {
            List {
                LabeledContent("DTCG format", value: "2025.10")
                LabeledContent("Resolved profile", value: catalog.profile)
                LabeledContent("Semantic paths", value: "\(catalog.allPaths.count)")
                LabeledContent("Apple touch minimum", value: "44 pt")
                LabeledContent("Android touch minimum", value: "48 dp")
            }
            .navigationTitle("Token contract")
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("Done") { dismiss() }
                }
            }
        }
    }
}

#Preview("Loaded · phone") {
    TokenGalleryView()
}

#Preview("Arabic · tablet", traits: .fixedLayout(width: 1024, height: 768)) {
    TokenGalleryView()
        .environment(\.layoutDirection, .rightToLeft)
}
