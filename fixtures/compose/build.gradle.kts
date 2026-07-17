plugins {
    id("com.android.application") version "9.2.0" apply false
    // Kotlin 2.x requires the Compose compiler plugin whenever Compose is enabled.
    id("org.jetbrains.kotlin.plugin.compose") version "2.3.10" apply false
}
