#include "buffer.h"

void buffer_append_uint32(uint8_t *buffer, uint32_t number, int32_t *index) {
  buffer[(*index)++] = (uint8_t)(number >> 24);
  buffer[(*index)++] = (uint8_t)(number >> 16);
  buffer[(*index)++] = (uint8_t)(number >> 8);
  buffer[(*index)++] = (uint8_t)number;
}

void buffer_append_int16(uint8_t *buffer, int16_t number, int32_t *index) {
  buffer[(*index)++] = (uint8_t)(number >> 8);
  buffer[(*index)++] = (uint8_t)number;
}

void buffer_append_float16(uint8_t *buffer, float number, float scale,
                           int32_t *index) {
  float x = number * scale;
  if (x > 32767.0f)
    x = 32767.0f;
  else if (x < -32767.0f)
    x = -32767.0f;
  buffer_append_int16(buffer, (int16_t)(x < 0.0f ? x - 0.5f : x + 0.5f), index);
}

uint32_t buffer_get_uint32(const uint8_t *buffer, int32_t *index) {
  uint32_t res = ((uint32_t)buffer[*index] << 24) |
                 ((uint32_t)buffer[*index + 1] << 16) |
                 ((uint32_t)buffer[*index + 2] << 8) | (uint32_t)buffer[*index + 3];
  *index += 4;
  return res;
}

int16_t buffer_get_int16(const uint8_t *buffer, int32_t *index) {
  int16_t res = (int16_t)(((uint16_t)buffer[*index] << 8) |
                          (uint16_t)buffer[*index + 1]);
  *index += 2;
  return res;
}

float buffer_get_float16(const uint8_t *buffer, float scale, int32_t *index) {
  return (float)buffer_get_int16(buffer, index) / scale;
}
