load("@rules_cc//cc:defs.bzl", "cc_library")
load("@rules_license//rules:license.bzl", "license")

package(default_applicable_licenses = [":license"])

license(
    name = "license",
    license_kinds = ["@rules_license//licenses/spdx:BSD-3-Clause"],
    license_text = "LICENSE",
)

cc_library(
    name = "double-conversion",
    srcs = glob(["double-conversion/*.cc"]),
    hdrs = glob(["double-conversion/*.h"]),
    includes = ["."],
    linkopts = ["-lm"],
    visibility = ["//visibility:public"],
)
