VESC_TOOL ?= vesc_tool
PKG := template.vescpkg

all: $(PKG)

$(PKG): ui.qml pkgdesc.qml README.md
	$(VESC_TOOL) --buildPkgFromDesc pkgdesc.qml

# Run the QML in a VESC Tool window with no controller attached. The host
# prepends the same imports it prepends before upload, so this is a faithful
# check of what the device will run.
preview:
	$(VESC_TOOL) --loadQml $(CURDIR)/ui.qml

# Run the descriptor's isCompatible() against a synthetic device.
compat: pkgdesc.qml
	$(VESC_TOOL) --buildPkgFromDesc pkgdesc.qml --testPkgDesc 'vesc:60:'

# Show the GUI that is currently stored on the connected controller.
preview-device:
	$(VESC_TOOL) --loadQmlVesc

clean:
	rm -f $(PKG)

.PHONY: all preview compat preview-device clean
