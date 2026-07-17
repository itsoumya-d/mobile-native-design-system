package com.example.tokengallery

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.requiredSize
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.ArrowForward
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.ErrorOutline
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.Menu
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.ShowChart
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CenterAlignedTopAppBar
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilledIconButton
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.ListItem
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.heading
import androidx.compose.ui.semantics.role
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.semantics.stateDescription
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import mobile.tokens.MobileTokens

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TokenGalleryApp(initialContent: ContentState = ContentState.Populated) {
    var state by remember { mutableStateOf(GalleryState(content = initialContent)) }
    TokenGalleryTheme(highContrast = state.highContrast) {
        val tokens = LocalGalleryTokens.current
        Scaffold(
            modifier = Modifier.fillMaxSize().imePadding(),
            containerColor = tokens.canvas,
            topBar = {
                CenterAlignedTopAppBar(
                    title = { Text("Token Gallery") },
                    navigationIcon = {
                        IconButton(onClick = { state = state.copy(sheetVisible = true) }) {
                            Icon(Icons.Default.Menu, "Open gallery navigation")
                        }
                    },
                    actions = {
                        IconButton(onClick = { state = state.copy(highContrast = !state.highContrast) }) {
                            Icon(Icons.Default.Settings, "Toggle high contrast")
                        }
                    },
                    colors = TopAppBarDefaults.centerAlignedTopAppBarColors(containerColor = tokens.canvas),
                )
            },
        ) { padding ->
            BoxWithConstraints(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding)
                    .padding(horizontal = tokens.gutter),
            ) {
                val columns = GalleryLayout.columnsFor(maxWidth.value, androidx.compose.ui.platform.LocalDensity.current.fontScale)
                val motion = MotionPolicy(state.reducedMotion)
                AnimatedVisibility(
                    visible = true,
                    enter = androidx.compose.animation.fadeIn(animationSpec = tween(motion.durationMillis)),
                    exit = androidx.compose.animation.fadeOut(animationSpec = tween(motion.durationMillis)),
                ) {
                    GalleryContent(
                        state = state,
                        columns = columns,
                        onState = { state = it },
                        onRetry = { state = state.reduce(GalleryAction.Retry) },
                    )
                }
            }
        }
        if (state.sheetVisible) {
            ModalBottomSheet(onDismissRequest = { state = state.copy(sheetVisible = false) }) {
                Text("Gallery navigation", modifier = Modifier.padding(24.dp), style = MaterialTheme.typography.titleLarge)
                ListItem(headlineContent = { Text("Components") }, supportingContent = { Text("Buttons, fields, cards, rows and states") })
                ListItem(headlineContent = { Text("Accessibility stress") }, supportingContent = { Text("Arabic, large type, high contrast and reduced motion") })
                Spacer(Modifier.height(24.dp))
            }
        }
        if (state.dialogVisible) {
            AlertDialog(
                onDismissRequest = { state = state.copy(dialogVisible = false) },
                title = { Text("Save this review?") },
                text = { Text("A dialog remains readable and actionable with large text and right-to-left layouts.") },
                confirmButton = { TextButton(onClick = { state = state.copy(dialogVisible = false) }) { Text("Save") } },
                dismissButton = { TextButton(onClick = { state = state.copy(dialogVisible = false) }) { Text("Cancel") } },
            )
        }
    }
}

@Composable
private fun GalleryContent(
    state: GalleryState,
    columns: Int,
    onState: (GalleryState) -> Unit,
    onRetry: () -> Unit,
) {
    val body: @Composable () -> Unit = {
        GallerySection("Financial wellbeing") {
            StatusCard()
        }
        GallerySection("Token scales") { TokenScales() }
        GallerySection("Native components") {
            ComponentSamples(state, onState, onRetry)
        }
        GallerySection("Accessibility stress state") {
            AccessibilityStress(state, onState)
        }
    }
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        item {
            if (columns == 2) {
                Row(horizontalArrangement = Arrangement.spacedBy(20.dp)) {
                    Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(16.dp)) {
                        GallerySection("Financial wellbeing") { StatusCard() }
                        GallerySection("Token scales") { TokenScales() }
                    }
                    Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(16.dp)) {
                        GallerySection("Native components") { ComponentSamples(state, onState, onRetry) }
                        GallerySection("Accessibility stress state") { AccessibilityStress(state, onState) }
                    }
                }
            } else {
                Column(verticalArrangement = Arrangement.spacedBy(16.dp)) { body() }
            }
        }
        item { Spacer(Modifier.height(24.dp)) }
    }
}

@Composable
private fun GallerySection(title: String, content: @Composable () -> Unit) {
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(title, style = MaterialTheme.typography.titleMedium, modifier = Modifier.semantics { heading() })
        content()
    }
}

@Composable
private fun StatusCard() {
    val tokens = LocalGalleryTokens.current
    Card(
        colors = CardDefaults.cardColors(containerColor = tokens.surface),
        shape = RoundedCornerShape(tokens.cardRadius),
        modifier = Modifier.fillMaxWidth(),
    ) {
        Row(Modifier.padding(20.dp), verticalAlignment = Alignment.CenterVertically) {
            Box(
                Modifier
                    .size(56.dp)
                    .clip(CircleShape)
                    .background(tokens.positive),
                contentAlignment = Alignment.Center,
            ) { Text("74", color = tokens.onPrimary, fontWeight = FontWeight.Bold) }
            Spacer(Modifier.width(16.dp))
            Column(Modifier.weight(1f)) {
                Text("Ready for a review", style = MaterialTheme.typography.titleMedium)
                Text("Your score improved 6 points this month.", color = tokens.secondary)
            }
            Icon(Icons.Default.ShowChart, "Positive trend", tint = tokens.positive)
        }
    }
}

@Composable
private fun TokenScales() {
    val tokens = LocalGalleryTokens.current
    val scale = MobileTokens.values("android")
    Card(colors = CardDefaults.cardColors(containerColor = tokens.surface)) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Text("Semantic color", style = MaterialTheme.typography.labelLarge)
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                listOf(tokens.primary, tokens.positive, tokens.warning, tokens.negative, tokens.informative).forEachIndexed { index, color ->
                    Box(Modifier.size(40.dp).clip(RoundedCornerShape(12.dp)).background(color).semantics { stateDescription = "Color swatch ${index + 1}" })
                }
            }
            HorizontalDivider()
            Text("Type scale", style = MaterialTheme.typography.labelLarge)
            Text("Large title", style = MaterialTheme.typography.headlineMedium)
            Text("Headline", style = MaterialTheme.typography.titleMedium)
            Text("Body text that wraps when user font scale is increased.", style = MaterialTheme.typography.bodyMedium)
            Row(verticalAlignment = Alignment.Bottom, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                listOf(4, 8, 12, 16, 24, 32).forEach { size ->
                    Box(Modifier.width(size.dp).height(size.dp).background(tokens.primary.copy(alpha = .75f)))
                }
            }
            HorizontalDivider()
            Text("Layout, shape & interaction", style = MaterialTheme.typography.labelLarge)
            Text("Spacing: ${listOf("0", "2", "4", "8", "12", "16", "20", "24", "32", "40", "48", "64").joinToString(" · ")} dp")
            Text("Radii: ${scale["radius.none"]}, ${scale["radius.small"]}, ${scale["radius.medium"]}, ${scale["radius.large"]}, ${scale["radius.extraLarge"]} dp")
            Text("Touch targets: minimum ${scale["touchTarget.minimum"]} dp · comfortable ${scale["touchTarget.comfortable"]} dp")
            Text("Layout: 4 / 8 / 12 columns · gutters ${scale["layout.gutter.compact"]} / ${scale["layout.gutter.medium"]} / ${scale["layout.gutter.expanded"]} dp")
            Text("Motion: instant 80 ms · fast 160 ms · standard 240 ms · slow 420 ms")
            Text("Elevation, stroke, opacity, icon and haptic tokens are applied through Material components.", color = tokens.secondary)
        }
    }
}

@Composable
private fun ComponentSamples(state: GalleryState, onState: (GalleryState) -> Unit, onRetry: () -> Unit) {
    val tokens = LocalGalleryTokens.current
    var note by remember { mutableStateOf("") }
    Card(colors = CardDefaults.cardColors(containerColor = tokens.surface)) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.CenterVertically) {
                Button(onClick = { onState(state.copy(dialogVisible = true)) }, modifier = Modifier.heightIn(min = tokens.touchTarget)) { Text("Review plan") }
                OutlinedButton(onClick = { onState(state.copy(content = ContentState.Loading)) }, modifier = Modifier.heightIn(min = tokens.touchTarget)) { Text("Load") }
                FilledIconButton(onClick = { onState(state.copy(sheetVisible = true)) }, modifier = Modifier.requiredSize(tokens.touchTarget)) { Icon(Icons.Default.Add, "Add a goal") }
            }
            OutlinedTextField(
                value = note,
                onValueChange = { note = it },
                label = { Text("Reflection") },
                supportingText = { Text("Text fields grow with content and type scale.") },
                modifier = Modifier.fillMaxWidth().heightIn(min = 52.dp),
            )
            when (state.content) {
                ContentState.Populated -> ListRows()
                ContentState.Loading -> AsyncState("Loading plans", tokens.informative) { CircularProgressIndicator(Modifier.size(28.dp), color = tokens.informative) }
                ContentState.Empty -> AsyncState("No plans yet", tokens.secondary) { Icon(Icons.Default.Info, "No plans") }
                ContentState.Error -> AsyncState("We could not load your plan", tokens.negative) {
                    Icon(Icons.Default.ErrorOutline, "Error")
                    TextButton(onClick = onRetry) { Text("Try again") }
                }
            }
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                TextButton(onClick = { onState(state.copy(content = ContentState.Empty)) }) { Text("Empty") }
                TextButton(onClick = { onState(state.copy(content = ContentState.Error)) }) { Text("Error") }
            }
        }
    }
}

@Composable
private fun ListRows() {
    val rows = listOf("Build a buffer" to "Two weeks of spending", "Review subscriptions" to "3 changes to consider")
    rows.forEachIndexed { index, (title, summary) ->
        ListItem(
            modifier = Modifier
                .fillMaxWidth()
                .heightIn(min = 56.dp)
                .clickable(role = Role.Button) {},
            headlineContent = { Text(title) },
            supportingContent = { Text(summary) },
            trailingContent = { Icon(Icons.Default.ArrowForward, "Open $title") },
        )
        if (index == 0) HorizontalDivider()
    }
}

@Composable
private fun AsyncState(label: String, color: Color, visual: @Composable () -> Unit) {
    Row(
        Modifier
            .fillMaxWidth()
            .heightIn(min = 96.dp)
            .semantics { stateDescription = label },
        horizontalArrangement = Arrangement.spacedBy(12.dp, Alignment.CenterHorizontally),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        visual()
        Text(label, color = color, maxLines = 2, overflow = TextOverflow.Ellipsis)
    }
}

@Composable
private fun AccessibilityStress(state: GalleryState, onState: (GalleryState) -> Unit) {
    val tokens = LocalGalleryTokens.current
    Card(colors = CardDefaults.cardColors(containerColor = tokens.surface)) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Text("الاتجاه من اليمين إلى اليسار • ₹ 12,480 • +6%", style = MaterialTheme.typography.bodyLarge)
            Text("Use Android font size 200% to validate reflow; status is always labeled, never color only.", color = tokens.secondary)
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("Reduced motion", modifier = Modifier.weight(1f))
                androidx.compose.material3.Switch(
                    checked = state.reducedMotion,
                    onCheckedChange = { onState(state.copy(reducedMotion = it)) },
                )
            }
            Text("Entrance translation: ${if (MotionPolicy(state.reducedMotion).usesEntranceTranslation) "enabled" else "removed"}", color = tokens.secondary)
        }
    }
}
