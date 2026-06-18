#include <quic/QuicConstants.h>

int main() {
  return quic::kDefaultUDPSendPacketLen > 0 ? 0 : 1;
}
