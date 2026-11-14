// Experimental. See SKILL.md in this directory before trusting it.
//
// Headless driver for the LispBM interpreter on a VESC, through vesc_tool's QML
// surface. Inject this file with:
//
//   xvfb-run -a vesc_tool --loadQml agent.qml --qmlAutoConn \
//       --vescPort /dev/ttyACM0 --retryConn
//
// Every line this script emits goes to stdout with a "qml: " prefix. Grep for
// "LBM|" and ignore the rest of the Qt chatter.
//
// Why a QML file: vesc_tool has no REPL on the command line. The GUI Lisp page
// (vesc_tool:pages/pagelisp.cpp) is a thin shell over VescIf.commands() and a
// CodeLoader, and --loadQml gives the same two objects without the GUI.
//
// Edit CONFIG below; do not add UI elements (nothing renders this).

import QtQuick 2.15
import Vedder.vesc.commands 1.0
import Vedder.vesc.codeloader 1.0   // without this import: "CodeLoader is not a type"

Item {
    id: root

    // ---- CONFIG -----------------------------------------------------------
    // Empty = do not touch the script in flash. Set to a .lbm source path to
    // erase + upload + run ~1 s after the port comes up. Destructive: it
    // replaces whatever is in flash.
    property string uploadPath: ""
    property bool   reduceLisp: false
    // Stats poll period. Device drops requests that overlap, so do not go fast.
    property int    statsIntervalMs: 1000
    // Exit with status 0 as soon as the upload finishes, so this can be used as a
    // one-shot CLI step. Verified: Qt.quit() from a --loadQml script exits cleanly.
    property bool   quitAfterUpload: false

    // ---- plumbing ---------------------------------------------------------
    property Commands cmd: VescIf ? VescIf.commands() : null

    CodeLoader {
        id: loader
        // lispErase() returns false while mVesc is null, so this must happen.
        Component.onCompleted: loader.setVesc(VescIf)
    }

    function log(tag, msg) {
        console.log("LBM|" + tag + "|" + msg)
    }

    // Send one REPL expression. The interpreter prints the value itself; the
    // sentinel brackets it so a caller can tell where the answer ends. Only
    // safe because serial traffic to one device is ordered.
    function repl(expr) {
        log("TX", expr)
        cmd.lispSendReplCmd(expr)
        cmd.lispSendReplCmd("(print \"<<END>>\")")
    }

    // Same as the GUI's "run selection": short text goes through the REPL,
    // long text must be streamed (vesc_tool:pages/pagelisp.cpp:369).
    function runBlock(text) {
        if (text.length > 400) loader.lispStreamString(text, 0)
        else cmd.lispSendReplCmd(text)
    }

    function upload(path) {
        log("STATE", "upload " + path)
        // lispUploadFromPath erases first; lispUploadString does not.
        var ok = loader.lispUploadFromPath(path, root.reduceLisp)
        log("STATE", "upload " + (ok ? "ok" : "FAILED"))
        if (ok) cmd.lispSetRunning(1)
    }

    // ---- device events ----------------------------------------------------
    Connections {
        target: root.cmd

        function onLispPrintReceived(str) { log("PRINT", str) }
        function onLispRunningResRx(ok) { log("RUNNING", ok) }
        function onLispStatsRxMap(stats) { log("STAT", JSON.stringify(stats)) }
        function onPlotInitReceived(xLabel, yLabel) { log("PLOTINIT", xLabel + "|" + yLabel) }
        function onPlotDataReceived(x, y) { log("PLOT", x + "|" + y) }
        function onLispStreamCodeRx(offset, res) { log("STREAM", offset + "|" + res) }
    }

    // ---- main loop --------------------------------------------------------
    property bool didUpload: false

    Timer {
        id: pollTimer
        interval: root.statsIntervalMs
        repeat: true
        running: true

        onTriggered: {
            // --qmlAutoConn reconnects every second; before that, cmd is dead.
            if (!root.cmd || !VescIf.isPortConnected())
                return

            if (!root.didUpload) {
                root.didUpload = true
                log("STATE", "connected")
                if (root.uploadPath !== "") {
                    root.upload(root.uploadPath)
                    if (root.quitAfterUpload)
                        Qt.quit()
                }
            }

            root.cmd.lispGetStats(true)
        }
    }

    Component.onCompleted: log("STATE", "harness loaded")
}
