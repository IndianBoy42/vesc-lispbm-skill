/* Panic-free, allocation-free byte helpers for the generated config parser.
 *
 * Big-endian on the wire: that is what VESC Tool's config channel uses, and
 * what confparser.c (generated) expects. The CAN frames in control/can_proto.h
 * are little-endian by their own protocol and do not use these.
 */
#pragma once

#include <stdint.h>

void buffer_append_uint32(uint8_t *buffer, uint32_t number, int32_t *index);
void buffer_append_int16(uint8_t *buffer, int16_t number, int32_t *index);
/* Signed 16-bit fixed point. Saturates instead of wrapping: a value outside
 * the XML range (possible when a parameter is set over CAN beyond what the
 * settings page represents) then reads back as the largest representable
 * value instead of the opposite sign. */
void buffer_append_float16(uint8_t *buffer, float number, float scale,
                           int32_t *index);

uint32_t buffer_get_uint32(const uint8_t *buffer, int32_t *index);
int16_t buffer_get_int16(const uint8_t *buffer, int32_t *index);
float buffer_get_float16(const uint8_t *buffer, float scale, int32_t *index);
