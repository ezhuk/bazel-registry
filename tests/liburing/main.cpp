#include <liburing.h>

int main() {
  return IO_URING_CHECK_VERSION(2, 15) ? 1 : 0;
}
