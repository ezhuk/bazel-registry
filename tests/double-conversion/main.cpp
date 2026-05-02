#include <double-conversion/double-conversion.h>

int main() {
  double_conversion::StringToDoubleConverter converter(
    double_conversion::StringToDoubleConverter::NO_FLAGS,
    0.0,
    0.0,
    nullptr,
    nullptr
  );

  int processed = 0;
  double value = converter.StringToDouble("3.5", 3, &processed);

  return value == 3.5 && processed == 3 ? 0 : 1;
}
