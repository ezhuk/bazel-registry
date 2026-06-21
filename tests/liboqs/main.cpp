#include <cstring>

#include <oqs/oqs.h>

int main() {
  return std::strcmp(OQS_version(), "0.15.0");
}
