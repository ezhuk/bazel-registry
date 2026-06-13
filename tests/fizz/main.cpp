#include <fizz/record/Types.h>

int main() {
  auto alert = fizz::AlertDescription::close_notify;
  return alert == fizz::AlertDescription::close_notify ? 0 : 1;
}
