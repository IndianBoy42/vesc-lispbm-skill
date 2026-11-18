/* The generated confparser.c includes this for package identity. Only the
 * name is used; the ABI number comes from code.c (ext-tail-abi).
 *
 * Bump PACKAGE_VERSION when the parameter set or the config wire layout
 * changes: it is folded into the generated signature, so a stale EEPROM
 * blob is rejected rather than misread into the wrong fields. */
#pragma once

#include "conf_default.h"

#define PACKAGE_NAME "Template"
#define PACKAGE_VERSION "1"
