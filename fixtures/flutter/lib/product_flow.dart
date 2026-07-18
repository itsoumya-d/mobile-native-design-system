import 'package:flutter/material.dart';

enum ProductLoadState { loading, empty, error, populated }

class ProductRepository {
  ProductRepository();

  Future<void> saveCheckIn(String note) async {}
}

class ProductFlowApp extends StatelessWidget {
  const ProductFlowApp({super.key, this.repository});

  final ProductRepository? repository;

  @override
  Widget build(BuildContext context) {
    final data = repository ?? ProductRepository();
    return MaterialApp(
      title: 'Financial wellbeing',
      initialRoute: '/sign-in',
      routes: {
        '/sign-in': (context) => const SignInScreen(),
        '/home': (context) => const HomeScreen(),
        '/detail': (context) => const DetailScreen(),
        '/check-in': (context) => CheckInFormScreen(repository: data),
        '/settings': (context) => const SettingsScreen(),
      },
    );
  }
}

class SignInScreen extends StatelessWidget {
  const SignInScreen({super.key});

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Welcome')),
    body: SafeArea(
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 480),
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  'Your next money decision, made calmer.',
                  style: Theme.of(context).textTheme.headlineMedium,
                ),
                const SizedBox(height: 24),
                FilledButton(
                  onPressed: () =>
                      Navigator.pushReplacementNamed(context, '/home'),
                  child: const Text('Continue securely'),
                ),
              ],
            ),
          ),
        ),
      ),
    ),
  );
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  ProductLoadState state = ProductLoadState.populated;

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(
      title: const Text('Today'),
      actions: [
        IconButton(
          tooltip: 'Open settings',
          onPressed: () => Navigator.pushNamed(context, '/settings'),
          icon: const Icon(Icons.settings_outlined),
        ),
      ],
    ),
    floatingActionButton: FloatingActionButton.extended(
      onPressed: () => Navigator.pushNamed(context, '/check-in'),
      icon: const Icon(Icons.add),
      label: const Text('Check in'),
    ),
    body: SafeArea(
      child: LayoutBuilder(
        builder: (context, constraints) {
          final horizontal = constraints.maxWidth >= 720 ? 48.0 : 16.0;
          return AnimatedSwitcher(
            duration: MediaQuery.disableAnimationsOf(context)
                ? Duration.zero
                : const Duration(milliseconds: 220),
            child: ListView(
              key: ValueKey(state),
              padding: EdgeInsets.fromLTRB(horizontal, 16, horizontal, 96),
              children: [
                Text(
                  'Available cash',
                  style: Theme.of(context).textTheme.labelLarge,
                ),
                Text(
                  '₹ 12,480',
                  style: Theme.of(context).textTheme.displaySmall,
                ),
                const SizedBox(height: 24),
                _content(context),
              ],
            ),
          );
        },
      ),
    ),
  );

  Widget _content(BuildContext context) {
    switch (state) {
      case ProductLoadState.loading:
        return Semantics(
          liveRegion: true,
          label: 'Loading plans',
          child: const Center(child: CircularProgressIndicator()),
        );
      case ProductLoadState.empty:
        return const _ProductMessage(
          icon: Icons.inbox_outlined,
          title: 'No plans yet',
          message: 'Create a small check-in when you are ready.',
        );
      case ProductLoadState.error:
        return _ProductMessage(
          icon: Icons.error_outline,
          title: 'Plans unavailable',
          message: 'Your existing data is safe.',
          action: TextButton(
            onPressed: () => setState(() => state = ProductLoadState.populated),
            child: const Text('Try again'),
          ),
        );
      case ProductLoadState.populated:
        return Column(
          children: [
            Card(
              child: ListTile(
                leading: const Icon(Icons.savings_outlined),
                title: const Text('Emergency buffer'),
                subtitle: const Text('Two weeks of essential spending'),
                trailing: const Icon(Icons.chevron_right),
                onTap: () => Navigator.pushNamed(context, '/detail'),
              ),
            ),
            ListTile(
              title: const Text('Review subscriptions'),
              subtitle: const Text('3 changes to consider'),
              onTap: () => _showFilterSheet(context),
            ),
          ],
        );
    }
  }

  Future<void> _showFilterSheet(BuildContext context) =>
      showModalBottomSheet<void>(
        context: context,
        showDragHandle: true,
        builder: (context) => const SafeArea(
          child: Padding(
            padding: EdgeInsets.all(24),
            child: Text('Choose which recommendations to review.'),
          ),
        ),
      );
}

class DetailScreen extends StatelessWidget {
  const DetailScreen({super.key});

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Emergency buffer')),
    body: const SafeArea(
      child: Padding(
        padding: EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Goal progress',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 12),
            LinearProgressIndicator(value: .64),
            SizedBox(height: 16),
            Text('You are 64% of the way to two weeks of essential spending.'),
          ],
        ),
      ),
    ),
  );
}

class CheckInFormScreen extends StatefulWidget {
  const CheckInFormScreen({super.key, required this.repository});

  final ProductRepository repository;

  @override
  State<CheckInFormScreen> createState() => _CheckInFormScreenState();
}

class _CheckInFormScreenState extends State<CheckInFormScreen> {
  final controller = TextEditingController();
  bool saving = false;

  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Weekly check-in')),
    body: SafeArea(
      child: ListView(
        padding: const EdgeInsets.all(24),
        children: [
          TextField(
            controller: controller,
            maxLines: 4,
            textInputAction: TextInputAction.done,
            decoration: const InputDecoration(
              labelText: 'What changed this week?',
              helperText: 'Do not include account numbers.',
            ),
          ),
          const SizedBox(height: 24),
          FilledButton(
            onPressed: saving
                ? null
                : () async {
                    setState(() => saving = true);
                    await widget.repository.saveCheckIn(controller.text);
                    if (context.mounted) Navigator.pop(context);
                  },
            child: Text(saving ? 'Saving…' : 'Save check-in'),
          ),
        ],
      ),
    ),
  );
}

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  bool reminders = true;

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Settings')),
    body: SafeArea(
      child: ListView(
        children: [
          SwitchListTile.adaptive(
            title: const Text('Weekly reminders'),
            subtitle: const Text('Friday at 9:00'),
            value: reminders,
            onChanged: (value) => setState(() => reminders = value),
          ),
          const ListTile(
            title: Text('Language'),
            subtitle: Text('English and Arabic fixture coverage'),
          ),
        ],
      ),
    ),
  );
}

class _ProductMessage extends StatelessWidget {
  const _ProductMessage({
    required this.icon,
    required this.title,
    required this.message,
    this.action,
  });

  final IconData icon;
  final String title;
  final String message;
  final Widget? action;

  @override
  Widget build(BuildContext context) => Semantics(
    container: true,
    child: Column(
      children: [
        Icon(icon, size: 40),
        const SizedBox(height: 12),
        Text(title, style: Theme.of(context).textTheme.titleLarge),
        Text(message, textAlign: TextAlign.center),
        ?action,
      ],
    ),
  );
}
