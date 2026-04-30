#include <sodium.h>

int main() {
  return sodium_init() < 0;
}
