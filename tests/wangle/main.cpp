#include <wangle/bootstrap/ServerBootstrap.h>
#include <wangle/channel/Pipeline.h>

using Pipeline = wangle::Pipeline<folly::IOBufQueue&, Message>;

int main() {
  auto server = wangle::ServerBootstrap<Pipeline>();
  return 0;
}
