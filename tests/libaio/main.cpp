#include <libaio.h>

#include <cstdio>

int main() {
  io_context_t ctx = 0;

  int ret = io_setup(1, &ctx);
  if (ret != 0) {
    std::fprintf(stderr, "io_setup failed: %d\n", ret);
    return 1;
  }

  ret = io_destroy(ctx);
  if (ret != 0) {
    std::fprintf(stderr, "io_destroy failed: %d\n", ret);
    return 1;
  }

  std::puts("libaio OK");
  return 0;
}
