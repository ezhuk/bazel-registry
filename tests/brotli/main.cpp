#include <brotli/decode.h>
#include <brotli/encode.h>

int main(void) {
  char const input[] = "hello brotli";
  uint8_t encoded[128];
  uint8_t decoded[128];

  size_t encoded_size = sizeof(encoded);
  size_t decoded_size = sizeof(decoded);

  if (!BrotliEncoderCompress(
      BROTLI_DEFAULT_QUALITY,
      BROTLI_DEFAULT_WINDOW,
      BROTLI_MODE_GENERIC,
      sizeof(input),
      (uint8_t const *)input,
      &encoded_size,
      encoded)) {
    return 1;
  }

  if (BrotliDecoderDecompress(
      encoded_size,
      encoded,
      &decoded_size,
      decoded) != BROTLI_DECODER_RESULT_SUCCESS) {
    return 1;
  }

  return 0;
}
