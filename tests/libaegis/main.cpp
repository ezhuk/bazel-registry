#include <aegis.h>

#include <cstdint>

int main() {
  if (aegis_init() != 0) {
    return 1;
  }

  uint8_t const left[16] = {};
  uint8_t const right[16] = {};

  return aegis128l_keybytes() == 16 && aegis_verify_16(left, right) == 0 ? 0 : 1;
}
