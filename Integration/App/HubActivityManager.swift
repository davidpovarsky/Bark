import ActivityKit
import Foundation

// App-owned lifecycle controller. Vendor sources remain untouched.
@available(iOS 17.0, *)
@MainActor
final class HubActivityManager {
    static let shared = HubActivityManager()
    private init() {}

    func start(shortcuts: [String], title: String = "Shortcuts Hub") async throws {
        let names = Array(Set(shortcuts.map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }.filter { !$0.isEmpty })).sorted()
        guard !names.isEmpty else { return }
        guard ActivityAuthorizationInfo().areActivitiesEnabled else { return }
        for activity in Activity<HubActivityAttributes>.activities {
            await activity.end(nil, dismissalPolicy: .immediate)
        }
        let attributes = HubActivityAttributes(title: title)
        let state = HubActivityAttributes.ContentState(shortcuts: Array(names.prefix(4)))
        _ = try Activity<HubActivityAttributes>.request(attributes: attributes, content: .init(state: state, staleDate: nil), pushType: nil)
    }

    func stop() async {
        for activity in Activity<HubActivityAttributes>.activities {
            await activity.end(nil, dismissalPolicy: .immediate)
        }
    }
}
