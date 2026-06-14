#include <folly/io/IOBufQueue.h>
#include <wangle/bootstrap/ServerBootstrap.h>
#include <wangle/channel/Pipeline.h>

#include <string>

struct Message {
  std::string data;
};

using Pipeline = wangle::Pipeline<folly::IOBufQueue&, Message>;

int main() {
  auto server = wangle::ServerBootstrap<Pipeline>();
  return 0;
}
