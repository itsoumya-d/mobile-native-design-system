# SwiftUI Token Gallery

Native iPhone and iPad fixture for the shared semantic token contract.

```bash
xcodegen generate
xcodebuild test -project TokenGallery.xcodeproj -scheme TokenGallery \
  -destination 'platform=iOS Simulator,name=iPhone 17 Pro'
```

The deployment target is iOS/iPadOS 17. Tests and screenshots are intended for
iPhone SE, iPhone 17 Pro, and iPad Pro 11-inch simulator profiles.
