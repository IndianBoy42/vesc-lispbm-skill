// Package description. VESC Tool reads this file to build the .vescpkg, and to
// decide whether the package is offered for the connected device.
//
// Build:   vesc_tool --buildPkgFromDesc pkgdesc.qml
// Test:    vesc_tool --buildPkgFromDesc pkgdesc.qml --testPkgDesc 'vesc:60:'
//
// Only these properties are read; anything else here is ignored by the builder
// (createPackageFromDescription in codeloader.cpp).

import QtQuick 2.15

Item {
    property string pkgName: "Template GUI"
    property string pkgDescriptionMd: "README.md"
    property string pkgQml: "ui.qml"
    property bool pkgQmlIsFullscreen: false
    property string pkgOutput: "template.vescpkg"

    // Paths in the properties above are resolved relative to the working
    // directory, so run the build from this directory.

    // Called with the connected device's FW_RX_PARAMS before install and in the
    // package store listing. Return false to hide the package for that device.
    function isCompatible(fwRxParams) {
        // Only devices whose main firmware is a VESC can store a QML app.
        return fwRxParams.hwTypeStr().toLowerCase() === "vesc"
    }
}
