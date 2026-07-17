package com.example.tokengallery

import android.graphics.Color as AndroidColor
import androidx.compose.material3.ColorScheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.ProvidableCompositionLocal
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.runtime.staticCompositionLocalOf
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import mobile.tokens.LocalMobileTheme
import mobile.tokens.MobileTheme

data class GalleryTokens(
    val canvas: Color,
    val surface: Color,
    val content: Color,
    val secondary: Color,
    val primary: Color,
    val onPrimary: Color,
    val positive: Color,
    val warning: Color,
    val negative: Color,
    val informative: Color,
    val border: Color,
    val cardRadius: Dp,
    val touchTarget: Dp,
    val gutter: Dp,
)

val LocalGalleryTokens: ProvidableCompositionLocal<GalleryTokens> = staticCompositionLocalOf {
    error("Gallery tokens were not provided")
}

private fun Map<String, String>.color(path: String) =
    Color(AndroidColor.parseColor(getValue(path)))

private fun Map<String, String>.dimension(path: String) = getValue(path).toFloat().dp

private fun GalleryTokens.asColorScheme(dark: Boolean): ColorScheme {
    return if (dark) {
        darkColorScheme(
            primary = primary,
            onPrimary = onPrimary,
            surface = surface,
            onSurface = content,
            background = canvas,
            onBackground = content,
        )
    } else {
        lightColorScheme(
            primary = primary,
            onPrimary = onPrimary,
            surface = surface,
            onSurface = content,
            background = canvas,
            onBackground = content,
        )
    }
}

@Composable
fun TokenGalleryTheme(
    highContrast: Boolean,
    content: @Composable () -> Unit,
) {
    val dark = isSystemInDarkTheme()
    val theme = MobileTheme(
        when {
            highContrast -> "highContrast"
            dark -> "dark"
            else -> "android"
        },
    )
    val values = theme.values
    val tokens = GalleryTokens(
        canvas = values.color("color.surface.canvas"),
        surface = values.color("color.surface.default"),
        content = values.color("color.content.primary"),
        secondary = values.color("color.content.secondary"),
        primary = values.color("color.action.primary"),
        onPrimary = values.color("color.action.onPrimary"),
        positive = values.color("color.status.positive"),
        warning = values.color("color.status.warning"),
        negative = values.color("color.status.negative"),
        informative = values.color("color.status.informative"),
        border = values.color("color.border.subtle"),
        cardRadius = values.dimension("component.card.radius"),
        touchTarget = values.dimension("touchTarget.minimum"),
        gutter = values.dimension("layout.gutter.compact"),
    )
    CompositionLocalProvider(LocalMobileTheme provides theme, LocalGalleryTokens provides tokens) {
        MaterialTheme(colorScheme = tokens.asColorScheme(dark = dark), content = content)
    }
}
