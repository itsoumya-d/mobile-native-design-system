package com.example.tokengallery

import androidx.activity.compose.BackHandler
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
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
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowForward
import androidx.compose.material.icons.filled.ErrorOutline
import androidx.compose.material.icons.filled.Inbox
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.ListItem
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.heading
import androidx.compose.ui.semantics.role
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.semantics.stateDescription
import androidx.compose.ui.unit.dp

enum class ProductRoute {
    SignIn,
    Home,
    Detail,
    CheckIn,
    Settings,
}

enum class ProductLoadState {
    Loading,
    Empty,
    Error,
    Populated,
}

class ProductRepository {
    fun saveCheckIn(note: String) {
        note.trim()
    }
}

class ProductNavigation(
    private val onNavigate: (ProductRoute) -> Unit,
    private val onBack: () -> Unit,
) {
    fun navigate(route: ProductRoute) = onNavigate(route)
    fun back() = onBack()
}

@Composable
fun ProductFlowApp(repository: ProductRepository = ProductRepository()) {
    var route by remember { mutableStateOf(ProductRoute.SignIn) }
    var history by remember { mutableStateOf(emptyList<ProductRoute>()) }
    val navigation = ProductNavigation(
        onNavigate = { next ->
            history = history + route
            route = next
        },
        onBack = {
            route = history.lastOrNull() ?: ProductRoute.Home
            history = history.dropLast(1)
        },
    )
    BackHandler(enabled = history.isNotEmpty()) { navigation.back() }

    TokenGalleryTheme(highContrast = false) {
        when (route) {
            ProductRoute.SignIn -> SignInScreen {
                route = ProductRoute.Home
                history = emptyList()
            }
            ProductRoute.Home -> HomeScreen(navigation)
            ProductRoute.Detail -> DetailScreen(navigation)
            ProductRoute.CheckIn -> CheckInFormScreen(repository, navigation)
            ProductRoute.Settings -> SettingsScreen(navigation)
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SignInScreen(onContinue: () -> Unit) {
    Scaffold(topBar = { TopAppBar(title = { Text("Welcome") }) }) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(24.dp),
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.Start,
        ) {
            Text(
                "Your next money decision, made calmer.",
                style = MaterialTheme.typography.headlineLarge,
                modifier = Modifier.semantics { heading() },
            )
            Spacer(Modifier.height(24.dp))
            Button(
                onClick = onContinue,
                modifier = Modifier.fillMaxWidth().heightIn(min = 48.dp),
            ) {
                Text("Continue securely")
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(navigation: ProductNavigation) {
    var loadState by remember { mutableStateOf(ProductLoadState.Populated) }
    var sheetVisible by remember { mutableStateOf(false) }
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Today") },
                actions = {
                    IconButton(onClick = { navigation.navigate(ProductRoute.Settings) }) {
                        Icon(Icons.Default.Settings, "Open settings")
                    }
                },
            )
        },
    ) { padding ->
        BoxWithConstraints(
            Modifier
                .fillMaxSize()
                .padding(padding),
        ) {
            val horizontal = if (maxWidth >= 720.dp) 48.dp else 16.dp
            LazyColumn(
                modifier = Modifier.fillMaxSize(),
                contentPadding = androidx.compose.foundation.layout.PaddingValues(
                    start = horizontal,
                    top = 16.dp,
                    end = horizontal,
                    bottom = 96.dp,
                ),
                verticalArrangement = Arrangement.spacedBy(16.dp),
            ) {
                item {
                    Text("Available cash", style = MaterialTheme.typography.labelLarge)
                    Text("₹ 12,480", style = MaterialTheme.typography.displaySmall)
                }
                item {
                    when (loadState) {
                        ProductLoadState.Loading -> ProductMessage("Loading plans") {
                            CircularProgressIndicator()
                        }
                        ProductLoadState.Empty -> ProductMessage("No plans yet") {
                            Icon(Icons.Default.Inbox, "No plans")
                        }
                        ProductLoadState.Error -> ProductMessage("Plans unavailable") {
                            Icon(Icons.Default.ErrorOutline, "Error")
                            TextButton(onClick = { loadState = ProductLoadState.Populated }) {
                                Text("Try again")
                            }
                        }
                        ProductLoadState.Populated -> {
                            Card(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .clickable(role = Role.Button) {
                                        navigation.navigate(ProductRoute.Detail)
                                    },
                                shape = RoundedCornerShape(20.dp),
                            ) {
                                ListItem(
                                    headlineContent = { Text("Emergency buffer") },
                                    supportingContent = { Text("Two weeks of essential spending") },
                                    trailingContent = {
                                        Icon(Icons.Default.ArrowForward, "Open details")
                                    },
                                )
                            }
                            ListItem(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .clickable(role = Role.Button) { sheetVisible = true },
                                headlineContent = { Text("Review subscriptions") },
                                supportingContent = { Text("3 changes to consider") },
                            )
                        }
                    }
                }
                item {
                    Button(
                        onClick = { navigation.navigate(ProductRoute.CheckIn) },
                        modifier = Modifier.fillMaxWidth().heightIn(min = 48.dp),
                    ) {
                        Text("Check in")
                    }
                }
            }
        }
    }
    if (sheetVisible) {
        ModalBottomSheet(onDismissRequest = { sheetVisible = false }) {
            Column(Modifier.padding(24.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Text("Recommendation filters", style = MaterialTheme.typography.titleLarge)
                Text("Choose which recommendations to review.")
                Button(onClick = { sheetVisible = false }) { Text("Done") }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DetailScreen(navigation: ProductNavigation) {
    Scaffold(
        topBar = { TopAppBar(title = { Text("Emergency buffer") }) },
    ) { padding ->
        Column(
            Modifier.padding(padding).padding(24.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
            Text("Goal progress", style = MaterialTheme.typography.titleMedium)
            LinearProgressIndicator(progress = { 0.64f }, modifier = Modifier.fillMaxWidth())
            Text("You are 64% of the way to two weeks of essential spending.")
            TextButton(onClick = navigation::back) { Text("Back to today") }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CheckInFormScreen(
    repository: ProductRepository,
    navigation: ProductNavigation,
) {
    var note by remember { mutableStateOf("") }
    var saving by remember { mutableStateOf(false) }
    Scaffold(
        modifier = Modifier.imePadding(),
        topBar = { TopAppBar(title = { Text("Weekly check-in") }) },
    ) { padding ->
        Column(
            Modifier.padding(padding).padding(24.dp),
            verticalArrangement = Arrangement.spacedBy(20.dp),
        ) {
            OutlinedTextField(
                value = note,
                onValueChange = { note = it },
                label = { Text("What changed this week?") },
                supportingText = { Text("Do not include account numbers.") },
                minLines = 3,
                modifier = Modifier.fillMaxWidth(),
            )
            Button(
                onClick = {
                    saving = true
                    repository.saveCheckIn(note)
                    navigation.navigate(ProductRoute.Home)
                },
                enabled = !saving,
                modifier = Modifier.fillMaxWidth().heightIn(min = 48.dp),
            ) {
                Text(if (saving) "Saving…" else "Save check-in")
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(navigation: ProductNavigation) {
    var reminders by remember { mutableStateOf(true) }
    Scaffold(topBar = { TopAppBar(title = { Text("Settings") }) }) { padding ->
        LazyColumn(Modifier.padding(padding)) {
            item {
                ListItem(
                    headlineContent = { Text("Weekly reminders") },
                    supportingContent = { Text("Friday at 9:00") },
                    trailingContent = {
                        Switch(
                            checked = reminders,
                            onCheckedChange = { reminders = it },
                        )
                    },
                )
            }
            item {
                ListItem(
                    headlineContent = { Text("Language") },
                    supportingContent = { Text("English and Arabic fixture") },
                )
            }
            item {
                TextButton(onClick = navigation::back) { Text("Done") }
            }
        }
    }
}

@Composable
private fun ProductMessage(
    title: String,
    visual: @Composable () -> Unit,
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .heightIn(min = 180.dp)
            .semantics { stateDescription = title },
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(12.dp, Alignment.CenterVertically),
    ) {
        visual()
        Text(title, style = MaterialTheme.typography.titleMedium)
    }
}
