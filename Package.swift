// swift-tools-version:5.3

import PackageDescription

let package = Package(
    name: "kivy-ios",
    products: [
        .library(
            name: "kivy-ios",
            targets: ["kivy-ios"]),
    ],
    targets: [
        .target(
            name: "kivy-ios",
            dependencies: []),
    ]
)
