// Runs a crosscheck job in the system WebKit (Safari's engine and its WebGPU): a WKWebView in a small window loads
// SERVER/?job=JOB, posts its WebContent and GPU process ids to the server for sampling, and reloads the page when it
// stops returning frames or its web process dies. Exits when the job has no frames left.
//
//   swiftc -O wk_host.swift -o wk_host
//   wk_host http://127.0.0.1:8737 JOB
import AppKit
import WebKit

func processIDs(named name: String) -> Set<Int32> {
    let p = Process()
    p.executableURL = URL(fileURLWithPath: "/usr/bin/pgrep")
    p.arguments = ["-f", name]
    let pipe = Pipe()
    p.standardOutput = pipe
    try? p.run()
    p.waitUntilExit()
    let out = String(data: pipe.fileHandleForReading.readDataToEndOfFile(), encoding: .utf8) ?? ""
    return Set(out.split(separator: "\n").compactMap { Int32($0) })
}

final class Host: NSObject, WKNavigationDelegate, WKUIDelegate {
    let server: String
    let job: String
    let web: WKWebView
    let window: NSWindow
    var gpuBefore: Set<Int32>
    var networkBefore: Set<Int32>
    var pids: [Int32: String] = [:]
    var doneAt: Date?

    init(server: String, job: String) {
        self.server = server
        self.job = job
        gpuBefore = processIDs(named: "com.apple.WebKit.GPU")
        networkBefore = processIDs(named: "com.apple.WebKit.Networking")
        let config = WKWebViewConfiguration()
        config.websiteDataStore = .nonPersistent()
        web = WKWebView(frame: CGRect(x: 0, y: 0, width: 480, height: 160), configuration: config)
        window = NSWindow(contentRect: CGRect(x: 40, y: 40, width: 480, height: 160), styleMask: [.titled], backing: .buffered, defer: false)
        super.init()
        window.title = "femtovg wasm crosscheck: \(job)"
        window.contentView = web
        window.orderFrontRegardless()
        web.navigationDelegate = self
        web.uiDelegate = self
        load()
        Timer.scheduledTimer(withTimeInterval: 5, repeats: true) { _ in self.watch() }
    }

    func load() {
        web.load(URLRequest(url: URL(string: "\(server)/?job=\(job)")!))
    }

    func log(_ s: String) {
        FileHandle.standardError.write("\(Date().timeIntervalSince1970) \(s)\n".data(using: .utf8)!)
    }

    func post(_ path: String, _ body: [String: Any]) {
        var req = URLRequest(url: URL(string: "\(server)\(path)?job=\(job)")!)
        req.httpMethod = "POST"
        req.httpBody = try? JSONSerialization.data(withJSONObject: body)
        URLSession.shared.dataTask(with: req).resume()
    }

    func postPids() {
        var procs: [String: String] = [:]
        if let web = web.value(forKey: "_webProcessIdentifier") as? Int32, web > 0 {
            procs[String(web)] = "webcontent:\(web)"
        }
        // The GPU process this view's pool uses (WKProcessPool SPI), or else every GPU process started since the host.
        let pool = web.configuration.processPool as NSObject
        if pool.responds(to: Selector(("_gpuProcessIdentifier"))),
           let gpu = pool.value(forKey: "_gpuProcessIdentifier") as? Int32, gpu > 0 {
            procs[String(gpu)] = "gpu-process:\(gpu)"
        } else {
            for pid in processIDs(named: "com.apple.WebKit.GPU").subtracting(gpuBefore) {
                procs[String(pid)] = "gpu-process?:\(pid)"
            }
        }
        for pid in processIDs(named: "com.apple.WebKit.Networking").subtracting(networkBefore) {
            procs[String(pid)] = "network:\(pid)"
        }
        procs[String(getpid())] = "host:\(getpid())"
        post("/pids", procs)
    }

    func watch() {
        postPids()
        URLSession.shared.dataTask(with: URL(string: "\(server)/status")!) { data, _, _ in
            guard let data, let all = try? JSONSerialization.jsonObject(with: data) as? [[String: Any]],
                  let s = all.first(where: { $0["name"] as? String == self.job }) else { return }
            let pending = s["pending"] as? Int ?? 0, inflight = s["inflight"] as? Int ?? 0
            let stalled = s["since_last_result_s"] as? Double ?? 0
            DispatchQueue.main.async {
                if pending == 0 && inflight == 0 {
                    // HOLD_S: stay this long with the page idle, its processes still sampled, before exiting.
                    let hold = Double(ProcessInfo.processInfo.environment["HOLD_S"] ?? "0") ?? 0
                    if self.doneAt == nil { self.doneAt = Date() }
                    if Date().timeIntervalSince(self.doneAt!) >= hold {
                        self.log("\(self.job) finished")
                        exit(0)
                    }
                    return
                }
                if (inflight > 0 || pending > 0) && stalled > Double(ProcessInfo.processInfo.environment["STALL_S"] ?? "150")! {
                    self.log("reload: stalled \(stalled) s")
                    self.post("/event", ["event": "driver-reload", "stalled_s": stalled])
                    self.load()
                }
            }
        }.resume()
    }

    func webViewWebContentProcessDidTerminate(_ webView: WKWebView) {
        log("web content process terminated")
        post("/event", ["event": "webcontent-terminated"])
        load()
    }

    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        postPids()
    }
}

let args = CommandLine.arguments
guard args.count == 3 else {
    print("usage: wk_host SERVER JOB")
    exit(1)
}
let app = NSApplication.shared
app.setActivationPolicy(.accessory)
let host = Host(server: args[1], job: args[2])
app.run()
