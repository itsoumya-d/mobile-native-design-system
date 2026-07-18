import SwiftUI

enum ProductRoute: String, CaseIterable, Hashable {
    case signIn
    case home
    case detail
    case checkIn
    case settings
}

enum ProductLoadState {
    case loading
    case empty
    case error
    case populated
}

@MainActor
final class ProductRepository {
    func saveCheckIn(_ note: String) async {
        _ = note.trimmingCharacters(in: .whitespacesAndNewlines)
    }
}

struct ProductFlowView: View {
    @State private var path: [ProductRoute] = []
    @State private var signedIn = false
    private let repository = ProductRepository()

    var body: some View {
        NavigationStack(path: $path) {
            Group {
                if signedIn {
                    HomeScreen(
                        onOpen: { route in path.append(route) }
                    )
                } else {
                    SignInScreen {
                        signedIn = true
                        path = []
                    }
                }
            }
            .navigationDestination(for: ProductRoute.self) { route in
                switch route {
                case .signIn, .home:
                    HomeScreen(onOpen: { path.append($0) })
                case .detail:
                    DetailScreen()
                case .checkIn:
                    CheckInFormScreen(repository: repository) {
                        path = []
                    }
                case .settings:
                    SettingsScreen()
                }
            }
        }
    }
}

struct SignInScreen: View {
    let onContinue: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 24) {
            Spacer()
            Text("Your next money decision, made calmer.")
                .font(.largeTitle.bold())
            Button("Continue securely", action: onContinue)
                .buttonStyle(.borderedProminent)
                .controlSize(.large)
                .accessibilityHint("Opens your financial wellbeing overview")
            Spacer()
        }
        .frame(maxWidth: 520)
        .padding(24)
        .navigationTitle("Welcome")
    }
}

struct HomeScreen: View {
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @State private var loadState: ProductLoadState = .populated
    @State private var filtersVisible = false

    let onOpen: (ProductRoute) -> Void

    var body: some View {
        ScrollView {
            LazyVStack(alignment: .leading, spacing: 20) {
                Text("Available cash")
                    .font(.headline)
                    .foregroundStyle(.secondary)
                Text("₹ 12,480")
                    .font(.largeTitle.bold())
                content
            }
            .frame(maxWidth: 720, alignment: .leading)
            .padding(24)
        }
        .safeAreaInset(edge: .bottom) {
            Button {
                onOpen(.checkIn)
            } label: {
                Label("Check in", systemImage: "plus")
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.borderedProminent)
            .controlSize(.large)
            .padding()
            .background(.bar)
        }
        .navigationTitle("Today")
        .toolbar {
            Button {
                onOpen(.settings)
            } label: {
                Image(systemName: "gearshape")
            }
            .accessibilityLabel("Open settings")
        }
        .sheet(isPresented: $filtersVisible) {
            FilterSheet()
                .presentationDetents([.medium])
        }
        .animation(
            reduceMotion ? nil : .easeOut(duration: 0.22),
            value: loadState
        )
    }

    @ViewBuilder
    private var content: some View {
        switch loadState {
        case .loading:
            ProgressView("Loading plans")
                .frame(maxWidth: .infinity, minHeight: 180)
        case .empty:
            ContentUnavailableView(
                "No plans yet",
                systemImage: "tray",
                description: Text("Create a small check-in when you are ready.")
            )
        case .error:
            ContentUnavailableView {
                Label("Plans unavailable", systemImage: "exclamationmark.triangle")
            } description: {
                Text("Your existing data is safe.")
            } actions: {
                Button("Try again") { loadState = .populated }
            }
        case .populated:
            VStack(spacing: 12) {
                Button {
                    onOpen(.detail)
                } label: {
                    HStack {
                        VStack(alignment: .leading) {
                            Text("Emergency buffer").font(.headline)
                            Text("Two weeks of essential spending")
                                .foregroundStyle(.secondary)
                        }
                        Spacer()
                        Image(systemName: "chevron.right")
                    }
                    .padding()
                    .frame(maxWidth: .infinity, minHeight: 72)
                    .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 18))
                }
                .buttonStyle(.plain)
                .accessibilityHint("Opens goal details")

                Button {
                    filtersVisible = true
                } label: {
                    LabeledContent("Review subscriptions", value: "3 changes")
                        .frame(minHeight: 52)
                }
                .buttonStyle(.plain)
            }
        }
    }
}

struct DetailScreen: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Goal progress").font(.headline)
            ProgressView(value: 0.64)
            Text("You are 64% of the way to two weeks of essential spending.")
            Spacer()
        }
        .padding(24)
        .navigationTitle("Emergency buffer")
    }
}

struct CheckInFormScreen: View {
    let repository: ProductRepository
    let onSaved: () -> Void

    @State private var note = ""
    @State private var saving = false

    var body: some View {
        Form {
            Section("What changed this week?") {
                TextField(
                    "Reflection",
                    text: $note,
                    axis: .vertical
                )
                .lineLimit(3...6)
                Text("Do not include account numbers.")
                    .font(.footnote)
                    .foregroundStyle(.secondary)
            }
            Button(saving ? "Saving…" : "Save check-in") {
                Task {
                    saving = true
                    await repository.saveCheckIn(note)
                    onSaved()
                }
            }
            .disabled(saving)
        }
        .navigationTitle("Weekly check-in")
    }
}

struct SettingsScreen: View {
    @State private var reminders = true

    var body: some View {
        Form {
            Toggle("Weekly reminders", isOn: $reminders)
            LabeledContent("Reminder time", value: "Friday at 9:00")
            LabeledContent("Language", value: "English and Arabic fixture")
        }
        .navigationTitle("Settings")
    }
}

private struct FilterSheet: View {
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationStack {
            List {
                Label("Highest impact", systemImage: "sparkles")
                Label("Quick wins", systemImage: "bolt")
            }
            .navigationTitle("Recommendation filters")
            .toolbar {
                Button("Done") { dismiss() }
            }
        }
    }
}
