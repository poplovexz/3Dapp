package com.anglephoto.app.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val Primary = Color(0xFF6366F1)
private val PrimaryDark = Color(0xFF4F46E5)
private val Accent = Color(0xFFE879F9)
private val Background = Color(0xFFF9FAFB)
private val Surface = Color(0xFFFFFFFF)

private val LightColorScheme = lightColorScheme(
    primary = Primary,
    onPrimary = Color.White,
    primaryContainer = PrimaryDark,
    onPrimaryContainer = Color.White,
    secondary = Accent,
    onSecondary = Color.White,
    background = Background,
    onBackground = Color(0xFF111827),
    surface = Surface,
    onSurface = Color(0xFF111827),
    error = Color(0xFFEF4444),
    onError = Color.White
)

private val DarkColorScheme = darkColorScheme(
    primary = Primary,
    onPrimary = Color.White,
    primaryContainer = PrimaryDark,
    onPrimaryContainer = Color.White,
    secondary = Accent,
    onSecondary = Color.White,
    background = Color(0xFF111827),
    onBackground = Color(0xFFF9FAFB),
    surface = Color(0xFF1F2937),
    onSurface = Color(0xFFF9FAFB),
    error = Color(0xFFEF4444),
    onError = Color.White
)

@Composable
fun AnglePhotoTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}
