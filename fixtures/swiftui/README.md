# SwiftUI Token Gallery

Native iPhone and iPad fixture for the shared semantic token contract.

```bash
xcodegen generate
xcodebuild test -project TokenGallery.xcodeproj -scheme TokenGallery \
  -destination 'platform=iOS Simulator,name=iPhone 17 Pro'
xcodebuild build-for-testing -project TokenGallery.xcodeproj \
  -scheme TokenGallery \
  -destination 'platform=iOS Simulator,name=iPad Pro 11-inch (M5)'
```

The deployment target is iOS/iPadOS 17. The production flow covers
authentication, home/list, detail, form, settings, sheets, async states,
adaptive layout, accessibility, and reduced motion. XCTest includes route,
token, and native `ImageRenderer` snapshot contracts. Runtime tests and
screenshots are intended for iPhone SE, iPhone 17 Pro, and iPad Pro 11-inch
simulator profiles.
