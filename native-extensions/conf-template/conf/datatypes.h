/* Parameter block the VESC Tool settings page edits and EEPROM persists.
 *
 * Rename points: the typedef name (it must equal <valString> in
 * conf/settings.xml), the field names and their order (they must equal the
 * <SerOrder> list in the XML, one field per transmittable param), and the
 * cDefine-based defaults in the generated conf_default.h.
 *
 * The field types are the generator's wire mapping: type 1 double with
 * vTx 7 -> float (16-bit fixed point with the XML's vTxDoubleScale),
 * type 2 int with vTx 4 -> 2-byte integer, type 5 bool -> 1 byte,
 * type 4 enum -> 1 byte (the enumNames index).
 */
#pragma once

#include <stdbool.h>
#include <stdint.h>

typedef enum {
  TEMPLATE_MODE_OFF = 0,
  TEMPLATE_MODE_ON = 1,
} template_mode_t;

typedef struct {
  float example_gain;
  int16_t example_cycles;
  bool example_enabled;
  template_mode_t example_mode;
} TemplateConfig;
