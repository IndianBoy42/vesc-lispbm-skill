// Experimental. See SKILL.md in this directory before trusting it.
//
// Driver.qml is the whole harness: connection, REPL queue, upload, stats and
// the commands.txt watcher. Two thin entry files load it:
//
//   agent.qml   headless. Hides its own window; the agent's only surfaces are
//               stdout (LBM| lines) and commands.txt.
//   panel.qml   the same driver plus a visible UI. One process then holds the
//               single TCP slot AND serves the agent, so a panel you drive and
//               an agent that probes never fight over the link. This exists
//               because "only one TCP client" otherwise forces a choice.
//
// Two modes, selected by the URL fragment in --vescPort:
//
//   daemon (default)  start once, leave it up for the whole session. Watches
//                     commands.txt; replies go to stdout as LBM|OUT| records.
//                     run.sh `ask` / `wait` block on those records, so callers
//                     never guess with sleeps.
//   once              run the queued work from config.json then exit 0.
//
// Both attach to a VESC Tool window YOU control, over that window's TCP server.
// The window is untouched: you watch everything in it while this runs.
//
// Prerequisite, in the window: Connection -> TCP Server -> "Enable TCP Server".
//
// Every line goes to stdout with a "qml: " prefix. Grep for "LBM|".
//
// Why a QML file: vesc_tool has no REPL on the command line. The GUI Lisp page
// (vesc_tool:pages/pagelisp.cpp) is a thin shell over VescIf.commands() and a
// CodeLoader, and --loadQml gives the same two objects in a scriptable process.

import QtQuick 2.15
import QtQuick.Window 2.2
import Vedder.vesc.commands 1.0
import Vedder.vesc.codeloader 1.0   // without this import: "CodeLoader is not a type"

Item {
    id: root

    // ---- CONFIG -----------------------------------------------------------
    // config.json next to this file overrides these; --vescPort / --canFwd win
    // over both. Format and keys: see config.example.json and SKILL.md.
    property string uploadPath: ""
    property bool   reduceLisp: false
    property var    expressions: []
    // Commands::lispGetStats self-throttles at 1 s, so shorter only burns wakeups.
    property int    statsIntervalMs: 1000
    // How often commands.txt is checked for new lines, in daemon mode.
    property int    pollFileMs: 400
    // daemon: stay up, hide the window, watch commands.txt.
    // once:   run config then exit 0.
    property string mode: "daemon"
    // Hide this window at startup. The script keeps running; nothing is drawn.
    property bool   hideWindow: true
    property bool   quitWhenDone: false
    // Poll stats continuously. Off by default: a record per second drowns the
    // command stream, and the GUI already shows values via Poll All. `:stats`
    // requests one sample on demand.
    property bool   stayConnected: false

    // ---- CAN --------------------------------------------------------------
    // -1 = the device the window is attached to. >= 0 = that CAN node: every
    // command is wrapped in COMM_FORWARD_CAN and the node's replies come back
    // through the attached ESC (vesc/comm/commands.c:731). One mCanId exists,
    // so the queue serialises: target is applied per item, never mid-flight.
    property int    canTarget: -1
    property var    canIds: []

    // ---- connection -------------------------------------------------------
    property string port: ""
    property int    canFwd: -1
    property bool   connecting: false
    property bool   shuttingDown: false
    property bool   ready: false

    // ---- plumbing ---------------------------------------------------------
    property Commands cmd: VescIf ? VescIf.commands() : null
    property string scriptDir: ""
    // Byte offset already consumed from commands.txt, and the line being built.
    property int    cmdOffset: 0
    property string cmdPartial: ""

    function log(tag, msg) {
        console.log("LBM|" + tag + "|" + msg)
    }

    function argValue(flag, fallback) {
        var a = Qt.application.arguments
        for (var i = 0; i < a.length - 1; i++)
            if (a[i] === flag) return a[i + 1]
        return fallback
    }

    // One structured record per event, so a caller can parse replies and stats
    // without unpacking "PRINT|..." strings. The shell wrapper filters stdout
    // down to LBM| lines; nothing is written to disk.
    // Every event also goes out as one JSON record, so a caller can parse
    // replies and stats without unpacking "PRINT|..." strings.
    function emit(obj) {
        obj.t = Date.now()
        log("OUT", JSON.stringify(obj))
    }

    // TELL THE SHELL SOMETHING. vesc_tool rejects unknown flags, so the only
    // channels out are stdout and files.
    function loadConfig() {
        // The script is injected with Qt.createQmlObject, so its base URL is
        // qrc:/res/qml/ and a relative XHR cannot reach the file. Derive the
        // directory from --loadQml, which therefore must be absolute.
        var p = argValue("--loadQml", "")
        if (p === "" || p.charAt(0) !== "/") {
            log("CONF", "skipped: pass --loadQml as an absolute path")
            return
        }
        scriptDir = p.substring(0, p.lastIndexOf("/"))

        var xhr = new XMLHttpRequest()
        xhr.onreadystatechange = function() {
            if (xhr.readyState !== XMLHttpRequest.DONE) return
            if (xhr.responseText !== "") {
                try {
                    var c = JSON.parse(xhr.responseText)
                } catch (e) {
                    log("CONF", "invalid: " + e)
                    return
                }
                if (c.uploadPath !== undefined) root.uploadPath = c.uploadPath
                if (c.reduceLisp !== undefined) root.reduceLisp = c.reduceLisp
                if (c.expr !== undefined) root.expressions = [].concat(c.expr)
                if (c.expressions !== undefined) root.expressions = c.expressions
                if (c.statsIntervalMs !== undefined) root.statsIntervalMs = c.statsIntervalMs
                if (c.pollFileMs !== undefined) root.pollFileMs = c.pollFileMs
                if (c.hideWindow !== undefined) root.hideWindow = c.hideWindow
                if (c.quitWhenDone !== undefined) root.quitWhenDone = c.quitWhenDone
                if (c.stayConnected !== undefined) root.stayConnected = c.stayConnected
                if (c.canFwd !== undefined) root.canFwd = c.canFwd
                if (c.port !== undefined) root.port = c.port
                log("CONF", "loaded")
            } else {
                log("CONF", "no config.json")
            }

            if (root.mode === "once") {
                for (var i = 0; i < root.expressions.length; i++)
                    repl(root.expressions[i])
                if (root.uploadPath !== "")
                    pendingUpload = root.uploadPath
            }

            if (root.mode === "daemon") {
                // Resume after whatever the previous process already handled,
                // so restarting the daemon does not replay old commands.
                var head = new XMLHttpRequest()
                head.onreadystatechange = function() {
                    if (head.readyState !== XMLHttpRequest.DONE) return
                    cmdOffset = head.responseText.length
                    log("STATE", "daemon watching commands.txt at offset " + cmdOffset)
                }
                head.open("GET", "file://" + scriptDir + "/commands.txt")
                head.send()
            }
        }
        xhr.open("GET", "file://" + scriptDir + "/config.json")
        xhr.send()
    }

    CodeLoader {
        id: loader
        Component.onCompleted: loader.setVesc(VescIf)
    }

    // ---- REPL -------------------------------------------------------------
    // The REPL runs one expression at a time. Firing expressions back to back
    // loses all but the first reply (measured: 3 of 4 lost); 700 ms between
    // sends answered 8/8. So everything is queued and serialised.
    property var    replQueue: []
    property bool   replBusy: false
    property int    replPaceMs: 700
    property int    replQuietMs: 700
    property int    replTimeoutMs: 3000
    property var    replReply: []
    property string replTag: ""
    property int    replTimeouts: 0
    property int    replLastTx: 0
    // Target of the command in flight, so replies and stats can be attributed.
    property int    replCan: -1
    property int    statsCan: -1

    // Point the shared Commands at one node. Called only when nothing is in
    // flight, because a late reply would otherwise be attributed to the wrong
    // node.
    function applyTarget(id) {
        if (!cmd) return
        if (id >= 0) cmd.setSendCan(true, id)
        else cmd.setSendCan(false, 0)
    }

    function repl(expr, tag, can) {
        var t = (can === undefined) ? root.canTarget : can
        replQueue = replQueue.concat([{ e: expr, tag: tag === undefined ? "" : tag, can: t }])
        pumpRepl()
    }

    function pumpRepl() {
        if (replBusy || uploading || replQueue.length === 0) return
        if (!cmd || !VescIf.isPortConnected()) return

        var now = Date.now()
        var wait = replPaceMs - (now - replLastTx)
        if (wait > 0) { replPaceTimer.interval = wait; replPaceTimer.restart(); return }

        var item = replQueue[0]
        replQueue = replQueue.slice(1)
        replBusy = true
        replReply = []
        replTag = item.tag
        replCan = item.can
        replLastTx = now
        applyTarget(item.can)
        log("TX", (item.can >= 0 ? "[can " + item.can + "] " : "") + item.e)
        emit({ k: "tx", expr: item.e, tag: item.tag, can: item.can })
        cmd.lispSendReplCmd(item.e)
    }

    function replFile(path, tag) {
        var xhr = new XMLHttpRequest()
        xhr.onreadystatechange = function() {
            if (xhr.readyState !== XMLHttpRequest.DONE) return
            if (xhr.status !== 200 && xhr.status !== 0) {
                log("STATE", "cannot read " + path)
                return
            }
            repl(xhr.responseText, tag)
        }
        xhr.open("GET", "file://" + (path.charAt(0) === "/" ? path : scriptDir + "/" + path))
        xhr.send()
    }

    // Same as the GUI's "run selection": short text goes through the REPL,
    // long text must be streamed (vesc_tool:pages/pagelisp.cpp:369).
    function runBlock(text) {
        if (text.length > 400) loader.lispStreamString(text, 0)
        else cmd.lispSendReplCmd(text)
    }

    property string pendingUpload: ""
    property bool   uploading: false
    property var    uploadQueue: []

    // Uploads block in nested event loops, so they get their own queue: a
    // REPL item must never be sent while a script is being written.
    function enqueueUpload(path, can) {
        var t = (can === undefined) ? root.canTarget : can
        uploadQueue = uploadQueue.concat([{ p: path, can: t }])
        pumpUploads()
    }

    function pumpUploads() {
        if (uploading || replBusy || uploadQueue.length === 0) return
        if (!cmd || !VescIf.isPortConnected()) return
        var it = uploadQueue[0]
        uploadQueue = uploadQueue.slice(1)
        applyTarget(it.can)
        upload(it.p, it.can)
    }

    function upload(path, can) {
        uploading = true
        log("STATE", "upload " + path + (can >= 0 ? " [can " + can + "]" : ""))
        var ok = loader.lispUploadFromPath(path, root.reduceLisp)
        log("STATE", "upload " + (ok ? "ok" : "FAILED"))
        emit({ k: "upload", path: path, ok: ok, can: can })
        if (ok) cmd.lispSetRunning(1)
        uploading = false
        pumpUploads()
        pumpRepl()
        maybeFinish()
    }

    // One-shot mode is done when nothing is queued, nothing is in flight, and
    // no upload is pending. Daemon mode never finishes.
    function maybeFinish() {
        if (mode !== "once" || !quitWhenDone) return
        if (replBusy || replQueue.length > 0) return
        if (uploadQueue.length > 0) return
        if (pendingUpload !== "" || uploading) return
        log("STATE", "queue drained, exiting")
        Qt.quit()
    }

    function connectNow() {
        if (connecting || port.indexOf("tcp://") !== 0) return
        connecting = true
        var rest = port.substring(6)
        var sep = rest.lastIndexOf(":")
        log("STATE", "connectTcp " + rest)
        VescIf.connectTcp(rest.substring(0, sep), parseInt(rest.substring(sep + 1)))
        connecting = false
    }

    // ---- commands.txt -----------------------------------------------------
    // Line protocol, one command per line:
    //   <expr>                REPL expression -> {k:"reply", lines:[...]}
    //   :run <path>           evaluate a file
    //   :upload <path>        erase + upload + run, path relative to this dir
    //   ":multi <a> ; <b>"    queue several expressions, split on ' ; '
    //   :stats                one stats sample from the current target
    //   :ping                 local liveness check
    //   :quit                 exit
    //   :can scan             enumerate CAN nodes -> {k:"can", ids:[...]}
    //   :can off              target the attached device again
    //   :can <id>             make <id> the target for following commands
    //   :can <id> <expr>      run <expr> on <id> only, session target unchanged
    //   :can all <expr>       run <expr> on every discovered node, one at a time
    //   :can upload <id> <p>  erase + upload + run <p> on <id>
    //   # ...                 comment, ignored
    function handleLine(line) {
        var s = line.replace(/^\s+|\s+$/g, "")
        if (s === "" || s.charAt(0) === "#") return

        emit({ k: "cmd", line: s })

        if (s.indexOf(":upload ") === 0) {
            enqueueUpload(resolve(s.substring(8).replace(/^\s+|\s+$/g, "")))
        } else if (s.indexOf(":run ") === 0) {
            replFile(s.substring(5).replace(/^\s+|\s+$/g, ""))
        } else if (s.indexOf(":multi ") === 0) {
            var parts = s.substring(7).split(" ; ")
            for (var i = 0; i < parts.length; i++) repl(parts[i])
        } else if (s === ":can off") {
            canTarget = -1
            emit({ k: "can", target: -1 })
        } else if (s.indexOf(":can ") === 0) {
            handleCan(s.substring(5).replace(/^\s+|\s+$/g, ""))
        } else if (s === ":stats") {
            statsCan = canTarget
            cmd.lispGetStats(true)
            // The reply arrives asynchronously; emit() is driven by the signal.
        } else if (s === ":cfg") {
            // Custom (VESC Tool) configuration pages, as the TOOL decoded
            // them: it fetches them on every connect (fwVersionReceived ->
            // customConfigGet), so this reports the end-to-end path without
            // needing the TCP port for a raw client. num 0 while connected
            // means the firmware never dispatched COMM_GET_CUSTOM_CONFIG to
            // the extension, which is exactly what hides the page in the GUI.
            var info = { k: "cfg", connected: VescIf.isPortConnected(),
                         num: VescIf.customConfigNum(),
                         loaded: VescIf.customConfigsLoaded() }
            if (info.num > 0) {
                var p = VescIf.customConfig(0)
                info.hasB0 = p.hasParam("b0_base")
                info.b0 = p.getParamDouble("b0_base")
                info.b0Min = p.getParamMinDouble("b0_base")
                info.b0Max = p.getParamMaxDouble("b0_base")
                info.hasPlotDiv = p.hasParam("plot_div")
                info.plotDiv = p.getParamDouble("plot_div")
                info.hasCanNode = p.hasParam("can_node")
            }
            emit(info)
        } else if (s === ":ping") {
            emit({ k: "pong", connected: VescIf.isPortConnected() })
        } else if (s === ":quit") {
            log("STATE", "quit requested")
            cleanShutdown()
            Qt.quit()
        } else {
            repl(s)
        }
    }

    // `:can` sub-commands. Prints are prefixed per node with set-print-prefix so
    // that several nodes printing into one console stay separable; that is also
    // why `all` costs two round trips per node.
    function handleCan(rest) {
        if (rest === "scan" || rest === "") {
            var ids = VescIf.scanCan()
            canIds = []
            for (var k = 0; k < ids.length; k++) canIds.push(ids[k])
            log("CAN", "scan -> [" + canIds.join(",") + "]")
            emit({ k: "can", ids: canIds })
            return
        }

        var m = rest.match(/^(\d+)\s*(.*)$/)
        if (m) {
            var id = parseInt(m[1])
            var tail = m[2]
            if (tail === "") {
                canTarget = id
                emit({ k: "can", target: id })
                repl("(set-print-prefix \"can" + id + "| \")", "", id)
                return
            }
            repl(tail, "", id)
            return
        }

        if (rest.indexOf("upload ") === 0) {
            var parts = rest.substring(7).match(/^(\d+)\s+(.+)$/)
            if (parts) enqueueUpload(resolve(parts[2]), parseInt(parts[1]))
            return
        }

        if (rest.indexOf("all ") === 0) {
            var expr = rest.substring(4)
            if (canIds.length === 0) {
                var found = VescIf.scanCan()
                canIds = []
                for (var j = 0; j < found.length; j++) canIds.push(found[j])
                emit({ k: "can", ids: canIds })
            }
            for (var i = 0; i < canIds.length; i++) {
                var cid = canIds[i]
                repl("(set-print-prefix \"can" + cid + "| \")", "", cid)
                repl(expr, "", cid)
            }
            return
        }

        log("CAN", "unrecognised: " + rest)
        emit({ k: "fault", why: "bad :can command", hint: ":can scan|off|<id>|<id> <expr>|all <expr>|upload <id> <path>" })
    }

    function resolve(p) {
        return p.charAt(0) === "/" ? p : scriptDir + "/" + p
    }

    function pollCommands() {
        if (scriptDir === "") return
        var xhr = new XMLHttpRequest()
        xhr.onreadystatechange = function() {
            if (xhr.readyState !== XMLHttpRequest.DONE) return
            if (xhr.status !== 200 && xhr.status !== 0) return
            var all = xhr.responseText

            // The file was truncated or replaced: start from the beginning.
            if (all.length < cmdOffset) {
                log("STATE", "commands.txt shrank, resetting offset")
                cmdOffset = 0
                cmdPartial = ""
            }
            if (all.length === cmdOffset) return

            var chunk = all.substring(cmdOffset)
            cmdOffset = all.length

            var lines = (cmdPartial + chunk).split("\n")
            // The last element is either "" (chunk ended on a newline) or a
            // half-written command that the writer has not finished; hold it.
            cmdPartial = lines.pop()
            for (var i = 0; i < lines.length; i++) handleLine(lines[i])
        }
        xhr.open("GET", "file://" + scriptDir + "/commands.txt")
        xhr.send()
    }

    // ---- timers & signals -------------------------------------------------
    Timer {
        id: replPaceTimer
        repeat: false
        onTriggered: pumpRepl()
    }

    Timer {
        id: replQuietTimer
        interval: root.replQuietMs
        repeat: false
        onTriggered: {
            if (!root.replBusy) return
            emit({ k: "reply", tag: root.replTag, can: root.replCan, lines: root.replReply })
            log("REPL", "done (" + root.replReply.length + " line(s))")
            root.replBusy = false
            pumpUploads()
            pumpRepl()
            maybeFinish()
        }
    }

    Timer {
        id: replTimeoutTimer
        interval: root.replTimeoutMs
        repeat: false
        running: root.replBusy
        onTriggered: {
            if (!root.replBusy || replQuietTimer.running) return
            root.replTimeouts++
            emit({ k: "reply", tag: root.replTag, can: root.replCan, lines: root.replReply, timeout: true })
            log("REPL", "timeout: no output in " + root.replTimeoutMs + "ms")

            // A silent link has exactly three known causes, and none of them
            // is the expression. Say so instead of leaving the caller to
            // debug a script that never ran.
            if (root.replTimeouts === 2) {
                // A silent link has a short list of causes. Which list depends
                // on whether the command was addressed to a CAN node.
                var hint = root.replCan >= 0
                    ? "no reply from CAN node " + root.replCan + " twice. Either that id is " +
                      "not on the bus (run :can scan), the node is unpowered or on a " +
                      "different bitrate, or the forwarding ESC lost the link."
                    : "no REPL output for two commands in a row. Either another " +
                      "client holds the window's single TCP slot (a panel, a " +
                      "second harness), the window's TCP server went stale after " +
                      "a client was killed (re-tick Connection -> TCP Server), or " +
                      "the device is mid-upload."
                emit({ k: "fault", why: "repl timeout x2", can: root.replCan, hint: hint })
                log("STATE", "suspect: " + (root.replCan >= 0
                    ? "CAN node " + root.replCan + " absent / wrong id"
                    : "TCP slot taken / stale server / upload in flight"))
            }

            root.replBusy = false
            pumpRepl()
        }
    }

    Timer {
        interval: 2000
        repeat: true
        running: !root.ready
        onTriggered: { if (!VescIf.isPortConnected()) root.connectNow() }
    }

    Timer {
        interval: root.pollFileMs
        repeat: true
        running: root.mode === "daemon" && root.ready
        onTriggered: pollCommands()
    }

    Timer {
        id: pollTimer
        interval: root.statsIntervalMs
        repeat: true
        running: true
        onTriggered: {
            if (!root.cmd) return

            // There is no disconnected signal on the QML side, so the only way
            // to notice a dropped TCP link is to look. Without this the
            // reconnect timer (running: !ready) stays disabled forever after
            // the first success and the session silently stops working.
            if (!VescIf.isPortConnected()) {
                if (root.ready) {
                    root.ready = false
                    log("STATE", "disconnected, will retry")
                    emit({ k: "disconnected" })
                }
                return
            }

            if (!root.ready) {
                root.ready = true
                emit({ k: "connected", port: root.port })
                log("STATE", "connected")

                if (root.canFwd >= 0) {
                    root.canTarget = root.canFwd
                    root.applyTarget(root.canTarget)
                    log("STATE", "canFwd " + root.canFwd)
                }
                if (root.pendingUpload !== "") {
                    root.upload(root.pendingUpload)
                    root.pendingUpload = ""
                }

                maybeFinish()
            }

            if (root.stayConnected)
                root.cmd.lispGetStats(true)
        }
    }

    Connections {
        target: root.cmd

        function onLispPrintReceived(str) {
            log("PRINT", str)
            if (root.replBusy) {
                root.replTimeouts = 0
                root.replReply = root.replReply.concat([str])
                replQuietTimer.restart()
            }
        }
        function onLispRunningResRx(ok) { log("RUNNING", ok) }
        function onLispStatsRxMap(stats) { emit({ k: "stats", can: root.statsCan, stats: stats }) }
        function onPlotInitReceived(xLabel, yLabel) { log("PLOTINIT", xLabel + "|" + yLabel) }
        function onPlotDataReceived(x, y) { emit({ k: "plot", x: x, y: y }) }
        function onLispStreamCodeRx(offset, res) { log("STREAM", offset + "|" + res) }
    }

    Component.onCompleted: {
        log("STATE", "harness loaded")
        port = argValue("--vescPort", "")
        var cf = argValue("--canFwd", "")
        if (cf !== "") canFwd = parseInt(cf)

        // Mode rides in the fragment of --vescPort ("tcp://host:port#once"),
        // because vesc_tool aborts on any flag it does not define. vescPort is
        // otherwise unused in this branch: connTimer only reads it for
        // --qmlAutoConn, which we never pass.
        var hash = port.indexOf("#")
        if (hash >= 0) {
            mode = port.substring(hash + 1)
            port = port.substring(0, hash)
        }

        if (port.indexOf("tcp://") !== 0) {
            log("STATE", "need --vescPort tcp://host:port; got [" + port + "]")
            Qt.quit()
            return
        }

        if (hideWindow && Window.window) {
            Window.window.visible = false
            log("STATE", "window hidden")
        }

        emit({ k: "hello", mode: mode, port: port })
        loadConfig()
        log("STATE", "target " + port + " canFwd=" + canFwd)
        connectNow()
    }

    // Close the TCP client before the process dies. A killed client leaves the
    // window's single-slot server accepting connections that relay nothing
    // (observed twice on real hardware), and a clean close is the only way to
    // avoid it. disconnectPort() flushes and closes the socket.
    function cleanShutdown() {
        if (shuttingDown) return
        shuttingDown = true
        if (VescIf && VescIf.isPortConnected()) {
            log("STATE", "closing TCP client")
            VescIf.disconnectPort()
        }
    }

    Component.onDestruction: cleanShutdown()
}
