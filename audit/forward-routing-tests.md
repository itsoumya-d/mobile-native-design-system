# Clean-Context Forward Routing Tests

The v2 router has a deterministic companion command:

```bash
python plugins/mobile-native-design-system/shared/scripts/mobile_route.py \
  "Understand every Flutter route and screen before suggesting changes."
```

`tests/test_v2_product_intelligence.py` runs the following prompt families
without project-specific answers or previously generated plans. Each decision
loads one focused skill, chooses at most one framework reference, and retains
explicit native-runtime rejections.

| Prompt family | Expected progressive route | Result |
|---|---|---|
| Whole-codebase Flutter discovery | `mobile-native-understand` + Flutter | Passed |
| Product-wide React Native roadmap | `mobile-native-plan` + React Native | Passed |
| SwiftUI accessibility and hierarchy review | `mobile-native-audit` + SwiftUI | Passed |
| Compose interruptible shared transition | `mobile-native-motion` + Compose | Passed |
| Flutter typed async component | `mobile-native-component-forge` + Flutter | Passed |
| Approved Kotlin screen in a dirty worktree | `mobile-native-implement` + Compose | Passed |
| Mobile redesign with no framework evidence | `mobile-native-understand`; request project evidence | Passed |
| Explicit Next.js/Tailwind/browser request | out-of-scope; load no mobile skill | Passed |

The router is intentionally conservative. It does not infer a framework from
generic “mobile” language, and it never authorizes implementation merely
because a request asks for a redesign.

The v1 release also recorded independent behavioral trials for Flutter async
checkout, SwiftUI iPad reduced motion, Compose parity, React Native motion
runtime translation, conditional Convex data boundaries, and an explicit web
request. Those observations remain useful historical evidence, while the v2
matrix above is the machine-enforced release gate.
