import AppIntents
import UserNotifications

@available(iOS 17.0, *)
struct StartHubActivityIntent: AppIntent {
    static let title: LocalizedStringResource = "Start Shortcuts Hub Live Activity"
    static var openAppWhenRun: Bool = false
    @Parameter(title: "Shortcut Names (comma separated)") var names: String
    func perform() async throws -> some IntentResult {
        try await HubActivityManager.shared.start(shortcuts: names.split(separator: ",").map(String.init))
        return .result()
    }
}

@available(iOS 17.0, *)
struct StopHubActivityIntent: AppIntent {
    static let title: LocalizedStringResource = "Stop Shortcuts Hub Live Activity"
    static var openAppWhenRun: Bool = false
    func perform() async throws -> some IntentResult {
        await HubActivityManager.shared.stop()
        return .result()
    }
}

@available(iOS 17.0, *)
struct HubAutomationAcknowledgedIntent: AppIntent {
    static let title: LocalizedStringResource = "Acknowledge Shortcuts Hub Automation"
    static var openAppWhenRun: Bool = false
    func perform() async throws -> some IntentResult {
        let center = UNUserNotificationCenter.current()
        let notifications = await center.deliveredNotifications()
        let ids = notifications.filter { $0.request.content.title == "Deflection" }.map { $0.request.identifier }
        center.removeDeliveredNotifications(withIdentifiers: ids)
        return .result()
    }
}
