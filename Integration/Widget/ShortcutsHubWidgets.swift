// Integration-owned adapter. Upstream Bark and Deflector files are untouched.
import ActivityKit
import AppIntents
import SwiftUI
import WidgetKit
import UserNotifications

@available(iOS 17.0, *)
struct HubShortcutIntent: AppIntent {
    static let title: LocalizedStringResource = "Trigger Shortcut Automation"
    static var openAppWhenRun: Bool = false
    @Parameter(title: "Shortcut Name") var shortcutName: String
    init() {}
    init(shortcutName: String) { self.shortcutName = shortcutName }
    func perform() async throws -> some IntentResult {
        guard !shortcutName.isEmpty else { return .result() }
        let content = UNMutableNotificationContent()
        content.title = "Deflection"
        content.body = shortcutName
        content.sound = nil
        content.interruptionLevel = .timeSensitive
        try await UNUserNotificationCenter.current().add(
            UNNotificationRequest(identifier: UUID().uuidString, content: content, trigger: nil)
        )
        return .result()
    }
}

@available(iOS 17.0, *)
struct HubActivityAttributes: ActivityAttributes {
    struct ContentState: Codable, Hashable {
        var shortcuts: [String]
    }
    var title: String
}

@available(iOS 17.0, *)
struct HubLiveActivityWidget: Widget {
    var body: some WidgetConfiguration {
        ActivityConfiguration(for: HubActivityAttributes.self) { context in
            VStack(alignment: .leading, spacing: 8) {
                Text(context.attributes.title).font(.headline)
                HStack {
                    ForEach(context.state.shortcuts, id: \.self) { name in
                        Button(intent: HubShortcutIntent(shortcutName: name)) {
                            Text(name).lineLimit(1)
                        }.buttonStyle(.bordered)
                    }
                }
            }.padding()
            .activityBackgroundTint(.black)
            .activitySystemActionForegroundColor(.white)
        } dynamicIsland: { context in
            DynamicIsland {
                DynamicIslandExpandedRegion(.center) {
                    HStack {
                        ForEach(context.state.shortcuts, id: \.self) { name in
                            Button(intent: HubShortcutIntent(shortcutName: name)) { Text(name) }
                        }
                    }
                }
            } compactLeading: {
                Image(systemName: "bolt.fill")
            } compactTrailing: {
                Text("Hub")
            } minimal: {
                Image(systemName: "bolt.fill")
            }
        }
    }
}

@available(iOS 17.0, *)
struct HubWidgetProvider: TimelineProvider {
    struct Entry: TimelineEntry { let date: Date }
    func placeholder(in context: Context) -> Entry { Entry(date: .now) }
    func getSnapshot(in context: Context, completion: @escaping (Entry) -> Void) { completion(Entry(date: .now)) }
    func getTimeline(in context: Context, completion: @escaping (Timeline<Entry>) -> Void) {
        completion(Timeline(entries: [Entry(date: .now)], policy: .never))
    }
}

@available(iOS 17.0, *)
struct HubShortcutWidget: Widget {
    var body: some WidgetConfiguration {
        StaticConfiguration(kind: "ShortcutsHubLauncher", provider: HubWidgetProvider()) { _ in
            VStack {
                Text("Shortcuts Hub").font(.headline)
                HStack {
                    Button(intent: HubShortcutIntent(shortcutName: "backup")) { Label("Backup", systemImage: "externaldrive") }
                    Button(intent: HubShortcutIntent(shortcutName: "lights")) { Label("Lights", systemImage: "lightbulb") }
                }.buttonStyle(.borderless)
            }.containerBackground(for: .widget) { Color(.systemBackground) }
        }
        .configurationDisplayName("Shortcuts Hub")
        .description("Trigger notification-based shortcut automations")
        .supportedFamilies([.systemMedium])
    }
}
