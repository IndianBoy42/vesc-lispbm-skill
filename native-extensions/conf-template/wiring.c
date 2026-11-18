/* Extension-side wiring for the generated settings page: copy these
 * sections into your code.c and rename the template symbols. This file is
 * documentation, not a compiled part of the template.
 *
 * Rename points: TemplateConfig, templateconfig in the generated symbol
 * names (confparser_*_templateconfig, TEMPLATECONFIG_SIGNATURE,
 * data_templateconfig_, DATA_TEMPLATECONFIG__SIZE), and the
 * template_apply_params hook that feeds your controller. */

/*--- parameter persistence (EEPROM) --------------------------------------
 * Layout: word 0 is the generated signature, words 1.. are the struct's
 * bytes (TemplateConfig is 4-byte aligned; pad trailing u16/u8 fields until
 * sizeof is a multiple of 4, or store the exact byte count). A signature
 * mismatch - different parameter set, or an EEPROM written by another
 * package - falls back to the compiled defaults instead of misreading
 * fields. Setting a parameter over CAN stays volatile by design: EEPROM
 * writes are slow and wear-limited, so the settings page is the
 * persistence path. */
#define TEMPLATE_EEPROM_SIG 0
#define TEMPLATE_EEPROM_DATA 1
#define TEMPLATE_EEPROM_WORDS ((sizeof(TemplateConfig) + 3u) / 4u)

static bool template_config_save(const TemplateConfig *cfg) {
  uint32_t words[TEMPLATE_EEPROM_WORDS];
  memset(words, 0, sizeof words);
  memcpy(words, cfg, sizeof *cfg);
  eeprom_var v;
  v.as_u32 = TEMPLATECONFIG_SIGNATURE;
  if (!VESC_IF->store_eeprom_var(&v, TEMPLATE_EEPROM_SIG))
    return false;
  for (uint32_t i = 0; i < TEMPLATE_EEPROM_WORDS; i++) {
    v.as_u32 = words[i];
    if (!VESC_IF->store_eeprom_var(&v, (int)(TEMPLATE_EEPROM_DATA + i)))
      return false;
  }
  return true;
}

/* False when no block or a foreign signature was found: keep defaults. */
static bool template_config_load(TemplateConfig *cfg) {
  uint32_t words[TEMPLATE_EEPROM_WORDS];
  eeprom_var v;
  if (!VESC_IF->read_eeprom_var(&v, TEMPLATE_EEPROM_SIG) ||
      v.as_u32 != TEMPLATECONFIG_SIGNATURE)
    return false;
  for (uint32_t i = 0; i < TEMPLATE_EEPROM_WORDS; i++) {
    if (!VESC_IF->read_eeprom_var(&v, (int)(TEMPLATE_EEPROM_DATA + i)))
      return false;
    words[i] = v.as_u32;
  }
  memcpy(cfg, words, sizeof *cfg);
  return true;
}

/*--- VESC Tool settings page ---------------------------------------------
 * get_cfg/set_cfg/get_cfg_xml have no context argument: reach the instance
 * through the loader's per-image slot, and fall back to the compiled
 * defaults while no instance exists (the page can be opened before the
 * script has created one, and must still render). */
static int template_cfg_get(uint8_t *buffer, bool is_default) {
  my_runtime_t *rt = my_state();
  if (is_default || !rt) {
    TemplateConfig def;
    confparser_set_defaults_templateconfig(&def);
    return confparser_serialize_templateconfig(buffer, &def);
  }
  return confparser_serialize_templateconfig(buffer, &rt->cfg);
}

static bool template_cfg_set(uint8_t *buffer) {
  TemplateConfig cfg;
  if (!confparser_deserialize_templateconfig(buffer, &cfg))
    return false; /* signature mismatch: not our parameter set */
  my_runtime_t *rt = my_state();
  if (rt) {
    VESC_IF->sys_lock();
    my_apply_params(&rt->ctrl, &cfg); /* your clamp-and-adopt hook */
    VESC_IF->sys_unlock();
  }
  return template_config_save(&cfg);
}

static int template_cfg_get_xml(uint8_t **buffer) {
  /* The image is linked at 0 and executes in place, so an address baked
   * into it is relative to the image base; PROG_ADDR is that base at
   * runtime. Keep the generated confxml.c const (the make conf rule
   * patches it) or the blob lands in .data, which a flash image must not
   * have. */
  *buffer = (uint8_t *)(uintptr_t)(data_templateconfig_ + PROG_ADDR);
  return DATA_TEMPLATECONFIG__SIZE;
}

/* In INIT_FUN, after the runtime exists and the EEPROM has been read: */
VESC_IF->conf_custom_add_config(template_cfg_get, template_cfg_set,
                                template_cfg_get_xml);
/* In stop(), so a re-open does not stack a second registration: */
VESC_IF->conf_custom_clear_configs();
