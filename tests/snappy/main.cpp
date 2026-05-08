#include <snappy.h>

#include <string>

int main() {
  const std::string input = "hello snappy";

  std::string compressed;
  snappy::Compress(input.data(), input.size(), &compressed);

  std::string uncompressed;
  if (!snappy::Uncompress(
    compressed.data(),
    compressed.size(),
    &uncompressed)) {
    return 1;
  }

  return input == uncompressed ? 0 : 1;
}
