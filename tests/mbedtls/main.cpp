#include <mbedtls/version.h>

int main() {
  return mbedtls_version_get_number() >= 0x04010000 ? 0 : 1;
}
