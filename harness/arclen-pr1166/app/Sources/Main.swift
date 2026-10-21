import UIKit
import Foundation
import os

let poiLog = OSLog(subsystem: "co.rbckr.arclenbench", category: .pointsOfInterest)
var currentSignpost = OSSignpostID(log: poiLog)
func marker(_ begin: Int32, _ name: UnsafePointer<CChar>?) {
    let text = name.map { String(cString: $0) } ?? ""
    if begin != 0 {
        currentSignpost = OSSignpostID(log: poiLog)
        os_signpost(.begin, log: poiLog, name: "frames", signpostID: currentSignpost, "%{public}s", text)
    } else {
        os_signpost(.end, log: poiLog, name: "frames", signpostID: currentSignpost, "%{public}s", text)
    }
}

/// Runs the text-on-path positioning kernel on the efficiency cores (background QoS) at launch and writes
/// Documents/arclen-<ARC_TAG>.csv. Environment (DEVICECTL_CHILD_ or xctrace --env): ARC_TAG, ARC_KINDS
/// ("straight-1000,cubic-1000"), ARC_VARIANTS (empty = all), ARC_ROUNDS, ARC_INNER, ARC_SIGNPOSTS=1, ARC_EXIT=1.
@main
class AppDelegate: UIResponder, UIApplicationDelegate {
    let label = UILabel()

    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        label.numberOfLines = 0
        label.textColor = .white
        label.font = UIFont.monospacedSystemFont(ofSize: 12, weight: .regular)
        label.text = "arclen bench: starting"
        UIApplication.shared.isIdleTimerDisabled = true
        let thread = Thread { self.run() }
        thread.name = "arclen-bench"
        thread.qualityOfService = .background
        thread.start()
        return true
    }

    func application(_ application: UIApplication, configurationForConnecting connectingSceneSession: UISceneSession, options: UIScene.ConnectionOptions) -> UISceneConfiguration {
        let configuration = UISceneConfiguration(name: nil, sessionRole: connectingSceneSession.role)
        configuration.delegateClass = SceneDelegate.self
        return configuration
    }

    func run() {
        pthread_set_qos_class_self_np(QOS_CLASS_BACKGROUND, 0)
        let env = ProcessInfo.processInfo.environment
        let tag = env["ARC_TAG"] ?? "run"
        let kinds = env["ARC_KINDS"] ?? "straight-1000"
        let variants = env["ARC_VARIANTS"] ?? ""
        let rounds = UInt32(env["ARC_ROUNDS"] ?? "20") ?? 20
        let inner = UInt32(env["ARC_INNER"] ?? "20") ?? 20
        let signposts: Int32 = env["ARC_SIGNPOSTS"] == "1" ? 1 : 0
        if let d = Double(env["ARC_DELAY_S"] ?? ""), d > 0 { Thread.sleep(forTimeInterval: d) }
        arclen_set_marker(marker)
        let docs = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let out = docs.appendingPathComponent("arclen-\(tag).csv")
        try? FileManager.default.removeItem(at: out)
        let started = Date()
        let thermalBefore = ProcessInfo.processInfo.thermalState.rawValue
        let rc = arclen_bench_run(out.path, kinds, variants, rounds, inner, signposts)
        let seconds = Date().timeIntervalSince(started)
        let meta = "tag=\(tag) kinds=\(kinds) variants=\(variants) rounds=\(rounds) inner=\(inner) rc=\(rc) seconds=\(String(format: "%.1f", seconds)) thermal_before=\(thermalBefore) thermal_after=\(ProcessInfo.processInfo.thermalState.rawValue)\n"
        try? meta.write(to: docs.appendingPathComponent("meta-\(tag).txt"), atomically: true, encoding: .utf8)
        print("arclen written \(out.path) \(meta)")
        DispatchQueue.main.async { self.label.text = "arclen \(tag) done in \(String(format: "%.1f", seconds)) s" }
        if env["ARC_EXIT"] == "1" {
            Thread.sleep(forTimeInterval: Double(env["ARC_EXIT_DELAY_S"] ?? "2") ?? 2)
            exit(0)
        }
    }
}

class SceneDelegate: UIResponder, UIWindowSceneDelegate {
    var window: UIWindow?
    func scene(_ scene: UIScene, willConnectTo session: UISceneSession, options connectionOptions: UIScene.ConnectionOptions) {
        guard let scene = scene as? UIWindowScene, let app = UIApplication.shared.delegate as? AppDelegate else { return }
        let window = UIWindow(windowScene: scene)
        let vc = UIViewController()
        vc.view.backgroundColor = .black
        app.label.frame = vc.view.bounds.insetBy(dx: 16, dy: 60)
        vc.view.addSubview(app.label)
        window.rootViewController = vc
        window.makeKeyAndVisible()
        self.window = window
    }
}
