// Experimental. Visible entry: the full Driver plus a small UI. See SKILL.md.
//
// WHY THIS EXISTS: the window's TCP server accepts exactly one client. If you
// point a separate panel at it, the panel takes that slot and the agent's REPL
// sends go nowhere (or the reverse). Running the driver *inside* the panel
// makes one process be both: you interact with the window, and commands.txt
// still reaches the same connection.
//
// Run it exactly like agent.qml, minus the hiding:
//
//   xvfb-run -a vesc_tool --loadQml <abs path>/panel.qml \
//       --vescPort tcp://127.0.0.1:65102
//
// (No Xvfb when you actually want to see it, obviously.)
//
// This is a TEMPLATE, not a product: replace the UI below with your own, keep
// the `Driver { ... }` root, and you keep the whole command protocol for free
// (`repl()`, `:upload`, stats, `run.sh ask`). Copy it out to your project —
// do not special-case the skill's copy for a specific device.

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.3

Driver {
    id: root
    hideWindow: false

    property var replyLog: []


    // Keep the last few reply records where the UI can show them.
    Connections {
        target: root.cmd
        function onLispPrintReceived(str) {
            root.replyLog = root.replyLog.concat([str]).slice(-6)
        }
    }

    Rectangle {
        anchors.fill: parent
        color: "#1b1b1b"

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 12
            spacing: 8

            Label {
                text: root.ready ? "connected: " + root.port : "not connected"
                color: root.ready ? "#7ee787" : "#f85149"
                font.bold: true
            }

            Repeater {
                model: root.replyLog
                Label {
                    text: modelData
                    color: "#d0d0d0"
                    font.family: "monospace"
                    Layout.fillWidth: true
                    elide: Text.ElideRight
                }
            }

            TextField {
                id: input
                Layout.fillWidth: true
                placeholderText: "LispBM expression, e.g. (get-rpm)"
                color: "white"
                onAccepted: { root.repl(text); clear() }
            }

            Button {
                text: "Send"
                onClicked: { if (input.text !== "") { root.repl(input.text); input.clear() } }
            }
        }
    }
}
