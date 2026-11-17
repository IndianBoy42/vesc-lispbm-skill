// Template for a GUI that lives on the controller and renders in any VESC Tool.
//
//   make preview     run this file in a window, no controller needed
//   make             build template.vescpkg
//   README.md        install steps and the portability rules
//
// The host prepends two imports before it instantiates this file:
//   import Vedder.vesc.vescinterface 1.0;   // gives VescIf on mobile
//   import "qrc:/mobile";                   // bundled components by name
// so `VescIf` and `Utility` resolve on desktop and on phones alike. Keep the
// file importable on its own as well; that is what makes `--loadQml` previews
// faithful.

import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.3

import Vedder.vesc.commands 1.0
import Vedder.vesc.utility 1.0

Item {
    id: root
    anchors.fill: parent

    // Read by the host to label the tab. Without it the tab is called "AppUi".
    property string tabTitle: "Template"

    // Live child object of VescIf. Grab it once; do not call the getter in bindings.
    // The guard costs nothing and silences the one TypeError the host prints when it
    // evaluates this binding before it has wired the context property.
    property Commands mCommands: VescIf ? VescIf.commands() : null

    // Theme colour with a fallback, for the same reason.
    function appColor(name) {
        return Utility ? Utility.getAppHexColor(name) : "#d7d7d7"
    }

    property bool connected: VescIf ? VescIf.isPortConnected() : false
    property real vIn: 0
    property real rpm: 0
    property real currentMotor: 0
    property real tempMos: 0
    property var lastCustomData: null
    property bool outputEnabled: false

    Connections {
        target: VescIf

        function onPortConnectedChanged() {
            root.connected = VescIf.isPortConnected()
            if (!root.connected) {
                root.stopOutput()
            }
        }
    }

    Connections {
        target: mCommands

        function onValuesReceived(values, mask) {
            root.vIn = values.v_in
            root.rpm = values.rpm
            root.currentMotor = values.current_motor
            root.tempMos = values.temp_mos
        }

        // Data sent by a LispBM script with (send-data ...).
        function onCustomAppDataReceived(data) {
            root.lastCustomData = data
        }
    }

    // Values arrive as signals only. Poll at a fixed rate; never per frame.
    Timer {
        interval: 100
        running: root.connected
        repeat: true
        onTriggered: root.mCommands.getValues()
    }

    function stopOutput() {
        outputEnabled = false
        dutySlider.value = 0
        mCommands.setCurrent(0)
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 12

        GridLayout {
            Layout.fillWidth: true
            columns: 2
            columnSpacing: 24
            rowSpacing: 6

            component Label: Text {
                color: root.appColor("normalText")
                font.pointSize: 11
            }

            component Value: Text {
                color: root.appColor("lightText")
                font.pointSize: 14
                font.bold: true
            }

            Label { text: "Battery" }
            Value { text: root.vIn.toFixed(1) + " V" }

            Label { text: "ERPM" }
            Value { text: Math.round(root.rpm) }

            Label { text: "Motor current" }
            Value { text: root.currentMotor.toFixed(1) + " A" }

            Label { text: "MOS temperature" }
            Value { text: root.tempMos.toFixed(1) + " °C" }
        }

        Rectangle {
            Layout.fillWidth: true
            implicitHeight: 1
            color: root.appColor("lightBackground")
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 12

            Button {
                text: root.outputEnabled ? "Release" : "Enable output"
                enabled: root.connected
                onClicked: {
                    if (root.outputEnabled) {
                        root.stopOutput()
                    } else {
                        root.outputEnabled = true
                    }
                }
            }

            Slider {
                id: dutySlider
                Layout.fillWidth: true
                from: -1
                to: 1
                value: 0
                enabled: root.outputEnabled && root.connected

                // Only steer while the handle is held; releasing stops the motor.
                onMoved: if (pressed) root.mCommands.setDutyCycle(value)
                onPressedChanged: {
                    if (!pressed) {
                        value = 0
                        root.mCommands.setCurrent(0)
                    }
                }
            }

            Value {
                Layout.preferredWidth: 64
                horizontalAlignment: Text.AlignRight
                text: dutySlider.value.toFixed(2)
            }
        }

        Label {
            Layout.fillWidth: true
            wrapMode: Text.Wrap
            text: root.connected
                  ? (root.lastCustomData
                     ? "Custom app data: " + root.lastCustomData.byteLength + " bytes"
                     : "Custom app data: none yet")
                  : "Not connected. Values stay at zero until VESC Tool connects."
        }

        Item { Layout.fillHeight: true }
    }
}
