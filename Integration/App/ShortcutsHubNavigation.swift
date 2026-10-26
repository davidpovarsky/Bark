import SwiftUI
import UIKit

/// Bark-owned entry point; Deflector's original MainView remains vendor-owned.
@available(iOS 26.0, *)
enum ShortcutsHubNavigation {
    static func makeController() -> UIViewController {
        let controller = UIHostingController(rootView: MainView())
        controller.title = "קיצורים"
        controller.tabBarItem = UITabBarItem(
            title: "קיצורים",
            image: UIImage(systemName: "square.grid.2x2"),
            tag: 3
        )
        return controller
    }
}
