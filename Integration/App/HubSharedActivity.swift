import ActivityKit
import Foundation

@available(iOS 17.0, *)
struct HubActivityAttributes: ActivityAttributes {
    struct ContentState: Codable, Hashable {
        var shortcuts: [String]
    }
    var title: String
}
