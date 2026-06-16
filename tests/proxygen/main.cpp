#include <proxygen/httpserver/HTTPServer.h>

int main() {
  proxygen::HTTPServerOptions options;
  options.threads = 1;
  return options.threads == 1 ? 0 : 1;
}
