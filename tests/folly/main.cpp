#include <folly/folly-config.h>

#include <iostream>

int main() {
#ifdef FOLLY_HAVE_PTHREAD
  std::cout << "FOLLY_HAVE_PTHREAD=1\n";
#else
  std::cout << "FOLLY_HAVE_PTHREAD=0\n";
#endif

#ifdef FOLLY_HAVE_LIBGLOG
  std::cout << "FOLLY_HAVE_LIBGLOG=1\n";
#else
  std::cout << "FOLLY_HAVE_LIBGLOG=0\n";
#endif

  return 0;
}
