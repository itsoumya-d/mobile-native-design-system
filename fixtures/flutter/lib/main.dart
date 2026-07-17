import 'package:flutter/material.dart';

import 'generated/mobile_theme_extension.dart';
import 'generated/mobile_tokens.dart';

void main() => runApp(const TokenGalleryApp());

/// The gallery deliberately keeps data local: it is a fixture for inspecting
/// the contract rather than a product screen backed by a service.
class TokenGalleryApp extends StatelessWidget {
  const TokenGalleryApp({super.key, this.reducedMotion = false});

  final bool reducedMotion;

  @override
  Widget build(BuildContext context) {
    final tokens = TokenValues.forProfile('base');
    final colors = ColorScheme.fromSeed(
      seedColor: tokens.color('color.action.primary'),
      brightness: Brightness.light,
      surface: tokens.color('color.surface.default'),
    );
    return MaterialApp(
      title: 'Token Gallery',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: colors,
        scaffoldBackgroundColor: tokens.color('color.surface.canvas'),
        extensions: const [MobileThemeExtension()],
        textTheme: ThemeData.light().textTheme.copyWith(
          displaySmall: tokens.textStyle('typography.largeTitle'),
          headlineMedium: tokens.textStyle('typography.title'),
          titleLarge: tokens.textStyle('typography.headline'),
          bodyLarge: tokens.textStyle('typography.body'),
          labelLarge: tokens.textStyle('typography.label'),
          bodySmall: tokens.textStyle('typography.caption'),
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: tokens.color('color.surface.default'),
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 16,
            vertical: 14,
          ),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(
              tokens.number('component.textField.radius'),
            ),
            borderSide: BorderSide(color: tokens.color('color.border.subtle')),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(
              tokens.number('component.textField.radius'),
            ),
            borderSide: BorderSide(
              color: tokens.color('color.border.focus'),
              width: tokens.number('component.textField.focusBorder'),
            ),
          ),
        ),
      ),
      home: GalleryScreen(forceReducedMotion: reducedMotion),
    );
  }
}

class GalleryLayout {
  const GalleryLayout._();

  static int columnsFor({required double width, required double textScale}) {
    return width >= 840 && textScale < 1.4 ? 2 : 1;
  }
}

class MotionPolicy {
  const MotionPolicy({required this.reduced});

  final bool reduced;
  Offset get entranceOffset => reduced ? Offset.zero : const Offset(0, 16);
  Duration get duration =>
      reduced ? Duration.zero : const Duration(milliseconds: 240);
}

class TokenValues {
  TokenValues.forProfile(String profile)
    : values = MobileTokens.profiles[profile] ?? MobileTokens.profiles['base']!;

  final Map<String, Object?> values;

  double number(String path) => (values[path] as num).toDouble();

  Color color(String path) {
    final raw = values[path]! as String;
    final hex = int.parse(raw.substring(1), radix: 16);
    return Color(raw.length == 7 ? hex | 0xFF000000 : hex);
  }

  TextStyle textStyle(String path) {
    final value = values[path]! as Map<String, Object?>;
    return TextStyle(
      fontSize: (value['fontSize']! as num).toDouble(),
      fontWeight: FontWeight.lerp(
        FontWeight.w400,
        FontWeight.w700,
        ((value['fontWeight']! as num).toDouble() - 400) / 300,
      ),
      letterSpacing: (value['letterSpacing']! as num).toDouble(),
      height:
          (value['lineHeight']! as num).toDouble() /
          (value['fontSize']! as num).toDouble(),
    );
  }
}

class GalleryScreen extends StatefulWidget {
  const GalleryScreen({super.key, required this.forceReducedMotion});

  final bool forceReducedMotion;

  @override
  State<GalleryScreen> createState() => _GalleryScreenState();
}

class _GalleryScreenState extends State<GalleryScreen> {
  bool _showStateSamples = true;

  @override
  Widget build(BuildContext context) {
    final tokens = TokenValues.forProfile('base');
    final media = MediaQuery.of(context);
    final reduced = widget.forceReducedMotion || media.disableAnimations;
    final motion = MotionPolicy(reduced: reduced);
    final width = media.size.width;
    final columns = GalleryLayout.columnsFor(
      width: width,
      textScale: media.textScaler.scale(1),
    );
    final horizontal = width >= 840
        ? tokens.number('layout.margin.expanded')
        : tokens.number('layout.margin.compact');

    return Scaffold(
      drawer: const _GalleryDrawer(),
      appBar: AppBar(
        leading: Builder(
          builder: (context) => Semantics(
            label: 'Open gallery navigation',
            button: true,
            child: IconButton(
              tooltip: 'Open gallery navigation',
              onPressed: Scaffold.of(context).openDrawer,
              icon: const ExcludeSemantics(child: Icon(Icons.menu)),
            ),
          ),
        ),
        title: const Text('Token Gallery'),
        actions: [
          Semantics(
            label: 'Open token details',
            button: true,
            child: IconButton(
              tooltip: 'Open token details',
              onPressed: () => _showDetails(context),
              icon: const ExcludeSemantics(child: Icon(Icons.info_outline)),
            ),
          ),
        ],
      ),
      body: SafeArea(
        child: AnimatedSlide(
          offset: motion.entranceOffset / 100,
          duration: motion.duration,
          curve: Curves.easeOutCubic,
          child: AnimatedOpacity(
            opacity: 1,
            duration: reduced
                ? Duration.zero
                : const Duration(milliseconds: 160),
            child: LayoutBuilder(
              builder: (context, constraints) => SingleChildScrollView(
                padding: EdgeInsetsDirectional.fromSTEB(
                  horizontal,
                  16,
                  horizontal,
                  32,
                ),
                child: Center(
                  child: ConstrainedBox(
                    constraints: BoxConstraints(
                      maxWidth: tokens.number('layout.contentMax'),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Text(
                          'Financial wellbeing',
                          style: Theme.of(context).textTheme.displaySmall,
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'A token-driven, accessible control inventory for iOS and Android.',
                          style: Theme.of(context).textTheme.bodyLarge,
                        ),
                        const SizedBox(height: 24),
                        _GalleryGrid(
                          columns: columns,
                          children: [
                            _ScalePanel(tokens: tokens),
                            _ButtonsPanel(
                              tokens: tokens,
                              onReview: () => _showPlanReview(context),
                            ),
                            _FieldAndCardsPanel(tokens: tokens),
                            const _RowsPanel(),
                          ],
                        ),
                        const SizedBox(height: 16),
                        Semantics(
                          toggled: _showStateSamples,
                          label: 'Toggle state samples',
                          child: SwitchListTile.adaptive(
                            title: const Text(
                              'States, motion, and accessibility stress',
                            ),
                            subtitle: const Text(
                              'Loading, empty, error, sheet, large text, RTL, and reduced motion',
                            ),
                            value: _showStateSamples,
                            onChanged: (value) =>
                                setState(() => _showStateSamples = value),
                          ),
                        ),
                        AnimatedSize(
                          duration: motion.duration,
                          alignment: AlignmentDirectional.topStart,
                          child: _showStateSamples
                              ? const _StateSamples()
                              : const SizedBox.shrink(),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Future<void> _showDetails(BuildContext context) {
    return showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      builder: (context) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Token details',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: 8),
              const Text('Source hash: ${MobileTokens.sourceHash}'),
              const SizedBox(height: 12),
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('Close'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _showPlanReview(BuildContext context) {
    return showDialog<void>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Plan review'),
        content: const Text('Your next small action is ready to review.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Done'),
          ),
        ],
      ),
    );
  }
}

class _GalleryDrawer extends StatelessWidget {
  const _GalleryDrawer();

  @override
  Widget build(BuildContext context) => Drawer(
    child: SafeArea(
      child: ListView(
        children: const [
          DrawerHeader(child: Text('Gallery navigation')),
          ListTile(leading: Icon(Icons.grid_view), title: Text('Overview')),
          ListTile(
            leading: Icon(Icons.palette_outlined),
            title: Text('Scales'),
          ),
          ListTile(
            leading: Icon(Icons.accessibility_new),
            title: Text('Accessibility'),
          ),
        ],
      ),
    ),
  );
}

class _GalleryGrid extends StatelessWidget {
  const _GalleryGrid({required this.columns, required this.children});
  final int columns;
  final List<Widget> children;

  @override
  Widget build(BuildContext context) {
    if (columns == 1) {
      return Column(
        children: children
            .map(
              (child) => Padding(
                padding: const EdgeInsets.only(bottom: 16),
                child: child,
              ),
            )
            .toList(),
      );
    }
    return Wrap(
      spacing: 16,
      runSpacing: 16,
      children: children
          .map(
            (child) => SizedBox(
              width: (MediaQuery.sizeOf(context).width - 96) / 2,
              child: child,
            ),
          )
          .toList(),
    );
  }
}

class _Panel extends StatelessWidget {
  const _Panel({required this.title, required this.child});
  final String title;
  final Widget child;

  @override
  Widget build(BuildContext context) => Card(
    child: Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 12),
          child,
        ],
      ),
    ),
  );
}

class _ScalePanel extends StatelessWidget {
  const _ScalePanel({required this.tokens});
  final TokenValues tokens;
  @override
  Widget build(BuildContext context) => _Panel(
    title: 'Scales',
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Spacing 0 · 2 · 4 · 8 · 12 · 16 · 20 · 24 · 32 · 40 · 48 · 64',
          style: Theme.of(context).textTheme.bodySmall,
        ),
        const SizedBox(height: 12),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            for (final path in [
              'color.action.primary',
              'color.action.secondary',
              'color.status.positive',
              'color.status.warning',
              'color.status.negative',
            ])
              Semantics(
                label: path,
                child: Container(
                  width: 40,
                  height: 40,
                  decoration: BoxDecoration(
                    color: tokens.color(path),
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
          ],
        ),
        const SizedBox(height: 16),
        Text('Large title', style: Theme.of(context).textTheme.displaySmall),
        Text('Headline', style: Theme.of(context).textTheme.titleLarge),
        Text(
          'Body and label scale with the system text setting.',
          style: Theme.of(context).textTheme.bodyLarge,
        ),
      ],
    ),
  );
}

class _ButtonsPanel extends StatelessWidget {
  const _ButtonsPanel({required this.tokens, required this.onReview});
  final TokenValues tokens;
  final VoidCallback onReview;
  @override
  Widget build(BuildContext context) => _Panel(
    title: 'Buttons',
    child: Wrap(
      spacing: 12,
      runSpacing: 12,
      crossAxisAlignment: WrapCrossAlignment.center,
      children: [
        SizedBox(
          height: tokens.number('sizing.control'),
          child: FilledButton.icon(
            onPressed: onReview,
            icon: const Icon(Icons.check_circle_outline),
            label: const Text('Review plan'),
          ),
        ),
        SizedBox(
          height: tokens.number('sizing.control'),
          child: OutlinedButton(
            onPressed: () {},
            child: const Text('Secondary'),
          ),
        ),
        Semantics(
          label: 'Adjust gallery tokens',
          button: true,
          child: SizedBox(
            width: tokens.number('component.iconButton.minimumSize'),
            height: tokens.number('component.iconButton.minimumSize'),
            child: IconButton(
              tooltip: 'Open token details',
              onPressed: () {},
              icon: const Icon(Icons.tune),
            ),
          ),
        ),
      ],
    ),
  );
}

class _FieldAndCardsPanel extends StatelessWidget {
  const _FieldAndCardsPanel({required this.tokens});
  final TokenValues tokens;
  @override
  Widget build(BuildContext context) => _Panel(
    title: 'Field and cards',
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const TextField(
          minLines: 1,
          maxLines: 3,
          decoration: InputDecoration(
            labelText: 'What would help you feel more confident?',
          ),
        ),
        const SizedBox(height: 16),
        Card.filled(
          color: tokens.color('color.surface.selected'),
          child: const Padding(
            padding: EdgeInsets.all(16),
            child: ListTile(
              leading: Icon(Icons.savings_outlined),
              title: Text('Savings buffer'),
              subtitle: Text('A small, repeatable step this week.'),
            ),
          ),
        ),
      ],
    ),
  );
}

class _RowsPanel extends StatelessWidget {
  const _RowsPanel();
  @override
  Widget build(BuildContext context) => _Panel(
    title: 'List rows',
    child: Column(
      children: const [
        ListTile(
          contentPadding: EdgeInsets.zero,
          minVerticalPadding: 12,
          leading: Icon(Icons.trending_up),
          title: Text('Progress'),
          subtitle: Text('Four actions complete'),
          trailing: Icon(Icons.chevron_right),
        ),
        Divider(),
        ListTile(
          contentPadding: EdgeInsets.zero,
          minVerticalPadding: 12,
          leading: Icon(Icons.notifications_none),
          title: Text('Check-in reminder'),
          subtitle: Text('Friday at 9:00'),
          trailing: Icon(Icons.chevron_right),
        ),
      ],
    ),
  );
}

class _StateSamples extends StatelessWidget {
  const _StateSamples();
  @override
  Widget build(BuildContext context) => _Panel(
    title: 'States and motion',
    child: Column(
      children: const [
        _StateRow(
          icon: Icons.autorenew,
          title: 'Loading',
          detail: 'Fetching your plan',
          busy: true,
        ),
        SizedBox(height: 12),
        _StateRow(
          icon: Icons.inbox_outlined,
          title: 'Empty',
          detail: 'No saved check-ins yet',
        ),
        SizedBox(height: 12),
        _ErrorRow(),
      ],
    ),
  );
}

class _StateRow extends StatelessWidget {
  const _StateRow({
    required this.icon,
    required this.title,
    required this.detail,
    this.busy = false,
  });
  final IconData icon;
  final String title;
  final String detail;
  final bool busy;
  @override
  Widget build(BuildContext context) => Semantics(
    liveRegion: busy,
    label: '$title: $detail',
    child: ListTile(
      contentPadding: EdgeInsets.zero,
      leading: busy
          ? const SizedBox(
              width: 28,
              height: 28,
              child: CircularProgressIndicator(),
            )
          : Icon(icon),
      title: Text(title),
      subtitle: Text(detail),
    ),
  );
}

class _ErrorRow extends StatefulWidget {
  const _ErrorRow();
  @override
  State<_ErrorRow> createState() => _ErrorRowState();
}

class _ErrorRowState extends State<_ErrorRow> {
  bool failed = true;
  @override
  Widget build(BuildContext context) => ListTile(
    contentPadding: EdgeInsets.zero,
    leading: Icon(failed ? Icons.error_outline : Icons.check_circle_outline),
    title: Text(failed ? 'Error' : 'Restored'),
    subtitle: Text(
      failed ? 'We could not refresh your plan.' : 'Your plan is available.',
    ),
    trailing: failed
        ? TextButton(
            onPressed: () => setState(() => failed = false),
            child: const Text('Try again'),
          )
        : null,
  );
}
