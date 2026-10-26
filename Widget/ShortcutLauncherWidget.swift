// Shortcuts Hub: interactive launcher based on Deflector's notification automation pattern.
// Attribution: https://github.com/Cizzuk/Deflector (MIT).
import AppIntents
import SwiftUI
import WidgetKit
import UserNotifications

@available(iOS 17.0, *)
struct LaunchShortcutNotificationIntent: AppIntent {
    static var title: LocalizedStringResource = "Launch Shortcut"
    static var description = IntentDescription("Triggers a user-configured notification automation.")
    static var openAppWhenRun = false

    @Parameter(title: "Shortcut Name") var shortcutName: String
    init() {}
    init(shortcutName: String) { self.shortcutName = shortcutName }

    func perform() async throws -> some IntentResult {
        guard !shortcutName.isEmpty else { return .result() }
        let center = UNUserNotificationCenter.current()
        let content = UNMutableNotificationContent()
        content.title = "Shortcuts Hub"
        content.body = shortcutName
        content.sound = nil
        content.interruptionLevel = .timeSensitive
        try await center.add(UNNotificationRequest(identifier: UUID().uuidString, content: content, trigger: nil))
        return .result()
    }
}

@available(iOS 17.0, *)
struct ShortcutLauncherWidget: Widget {
    let kind = "ShortcutLauncherWidget"
    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: ShortcutLauncherProvider()) { _ in
            VStack(spacing: 10) {
                Text("Shortcuts Hub").font(.headline)
                HStack(spacing: 18) {
                    Button(intent: LaunchShortcutNotificationIntent(shortcutName: "backup")) {
                        Label("Backup", systemImage: "externaldrive.fill")
                    }
                    Button(intent: LaunchShortcutNotificationIntent(shortcutName: "lights")) {
                        Label("Lights", systemImage: "lightbulb.fill")
                    }
                }.buttonStyle(.borderless)
            }.containerBackground(for: .widget) { Color(.systemBackground) }
        }
        .configurationDisplayName("Shortcuts Hub")
        .description("Run configured notification-triggered shortcuts")
        .supportedFamilies([.systemMedium])
    }
}

@available(iOS 17.0, *)
struct ShortcutLauncherProvider: TimelineProvider {
    struct Entry: TimelineEntry { let date: Date }
    func placeholder(in context: Context) -> Entry { Entry(date: .now) }
    func getSnapshot(in context: Context, completion: @escaping (Entry) -> Void) { completion(Entry(date: .now)) }
    func getTimeline(in context: Context, completion: @escaping (Timeline<Entry>) -> Void) {
        completion(Timeline(entries: [Entry(date: .now)], policy: .never))
    }
}
