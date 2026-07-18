import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
  AccessibilityInfo,
  ActivityIndicator,
  Animated,
  I18nManager,
  Modal,
  Platform,
  Pressable,
  ScrollView,
  StatusBar,
  StyleSheet,
  Text,
  TextInput,
  useColorScheme,
  useWindowDimensions,
  View,
  type TextStyle,
  type ViewStyle,
} from 'react-native';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import { createMobileTheme } from './src/generated/theme';
import { ProductFlow } from './src/ProductFlow';

type GalleryState = 'loading' | 'empty' | 'error' | 'ready';
type LayoutMode = 'compact' | 'medium' | 'expanded';
type TokenValues = Record<string, unknown>;

export function layoutModeForWidth(width: number): LayoutMode {
  if (width >= 840) return 'expanded';
  if (width >= 600) return 'medium';
  return 'compact';
}

export function motionSettingsFor(reduceMotion: boolean) {
  return reduceMotion
    ? { duration: 0, distance: 0 }
    : { duration: 240, distance: 16 };
}

function useReduceMotion() {
  const [reduceMotion, setReduceMotion] = useState(false);

  useEffect(() => {
    let active = true;
    AccessibilityInfo.isReduceMotionEnabled().then(enabled => {
      if (active) setReduceMotion(enabled);
    });
    const subscription = AccessibilityInfo.addEventListener(
      'reduceMotionChanged',
      setReduceMotion,
    );
    return () => {
      active = false;
      subscription.remove();
    };
  }, []);

  return reduceMotion;
}

function GalleryText({
  children,
  style,
  tone = 'primary',
  ...props
}: React.ComponentProps<typeof Text> & {
  tone?: 'primary' | 'secondary' | 'inverse';
}) {
  return (
    <Text
      {...props}
      allowFontScaling
      maxFontSizeMultiplier={2}
      style={[styles.text, toneStyles[tone], style]}
    >
      {children}
    </Text>
  );
}

function Action({
  label,
  onPress,
  background,
  color,
  accessibilityLabel = label,
  outlined = false,
}: {
  label: string;
  onPress: () => void;
  background: string;
  color: string;
  accessibilityLabel?: string;
  outlined?: boolean;
}) {
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={accessibilityLabel}
      onPress={onPress}
      style={({ pressed }) => [
        styles.action,
        { backgroundColor: background, opacity: pressed ? 0.86 : 1 },
        outlined && styles.actionOutlined,
      ]}
    >
      <GalleryText
        tone={color === '#FFFFFF' ? 'inverse' : 'primary'}
        style={[styles.actionText, { color }]}
      >
        {label}
      </GalleryText>
    </Pressable>
  );
}

function IconAction({
  label,
  symbol,
  onPress,
  color,
}: {
  label: string;
  symbol: string;
  onPress: () => void;
  color: string;
}) {
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={label}
      onPress={onPress}
      hitSlop={8}
      style={({ pressed }) => [
        styles.iconAction,
        { borderColor: color, opacity: pressed ? 0.86 : 1 },
      ]}
    >
      <GalleryText style={[styles.icon, { color }]}>{symbol}</GalleryText>
    </Pressable>
  );
}

function Section({
  title,
  children,
  color,
}: {
  title: string;
  children: React.ReactNode;
  color: string;
}) {
  return (
    <View accessibilityRole="summary" style={styles.section}>
      <GalleryText style={[styles.sectionTitle, { color }]}>
        {title}
      </GalleryText>
      {children}
    </View>
  );
}

function StatePreview({
  state,
  onRetry,
  t,
}: {
  state: GalleryState;
  onRetry: () => void;
  t: TokenValues;
}) {
  const primary = String(t['color.action.primary']);
  const secondary = String(t['color.content.secondary']);
  const error = String(t['component.state.errorColor']);

  if (state === 'loading') {
    return (
      <View accessibilityLabel="Loading plan" style={styles.statePreview}>
        <ActivityIndicator color={primary} />
        <GalleryText style={{ color: secondary }}>
          Loading your plan…
        </GalleryText>
      </View>
    );
  }
  if (state === 'empty') {
    return (
      <View accessibilityLabel="Empty plan" style={styles.statePreview}>
        <GalleryText style={[styles.stateIcon, { color: primary }]}>
          ◌
        </GalleryText>
        <GalleryText style={styles.stateTitle}>No planned payments</GalleryText>
        <GalleryText style={{ color: secondary }}>
          Your schedule will appear here when it is ready.
        </GalleryText>
      </View>
    );
  }
  if (state === 'error') {
    return (
      <View accessibilityLabel="Plan refresh error" style={styles.statePreview}>
        <GalleryText style={[styles.stateIcon, { color: error }]}>
          !
        </GalleryText>
        <GalleryText style={styles.stateTitle}>
          We could not refresh your plan
        </GalleryText>
        <Action
          label="Retry"
          accessibilityLabel="Retry plan refresh"
          onPress={onRetry}
          background={primary}
          color={String(t['color.action.onPrimary'])}
        />
      </View>
    );
  }
  return (
    <View accessibilityLabel="Ready plan" style={styles.statePreview}>
      <GalleryText style={styles.stateTitle}>Next planned payment</GalleryText>
      <GalleryText style={[styles.balance, { color: primary }]}>
        $240.00
      </GalleryText>
      <GalleryText style={{ color: secondary }}>
        Friday, June 28 · Rent fund
      </GalleryText>
    </View>
  );
}

function AppContent() {
  const colorScheme = useColorScheme();
  const { width } = useWindowDimensions();
  const reduceMotion = useReduceMotion();
  const [state, setState] = useState<GalleryState>('ready');
  const [modalVisible, setModalVisible] = useState(false);
  const [activeTab, setActiveTab] = useState('Gallery');
  const [query, setQuery] = useState('Emergency fund');
  const [noticeVisible, setNoticeVisible] = useState(true);
  const entrance = useRef(new Animated.Value(0)).current;
  const mode = layoutModeForWidth(width);
  const rtl = I18nManager.isRTL;
  const profile =
    colorScheme === 'dark' ? 'dark' : Platform.OS === 'ios' ? 'ios' : 'android';
  const t = createMobileTheme(profile).values as TokenValues;
  const motion = motionSettingsFor(reduceMotion);
  const colors = {
    canvas: String(t['color.surface.canvas']),
    card: String(t['component.card.background']),
    primary: String(t['color.action.primary']),
    onPrimary: String(t['color.action.onPrimary']),
    primaryText: String(t['color.content.primary']),
    secondaryText: String(t['color.content.secondary']),
    border: String(t['color.border.subtle']),
    selected: String(t['color.surface.selected']),
  };
  const direction: ViewStyle['flexDirection'] = rtl ? 'row-reverse' : 'row';
  const textAlign: TextStyle['textAlign'] = rtl ? 'right' : 'left';
  const tokenEntries = useMemo(() => Object.entries(t), [t]);

  useEffect(() => {
    entrance.setValue(0);
    Animated.timing(entrance, {
      toValue: 1,
      duration: motion.duration,
      useNativeDriver: true,
    }).start();
  }, [entrance, motion.duration]);

  const hideNotice = () => {
    Animated.timing(entrance, {
      toValue: 0,
      duration: motion.duration,
      useNativeDriver: true,
    }).start(() => setNoticeVisible(false));
  };

  return (
    <SafeAreaView
      style={[styles.safeArea, { backgroundColor: colors.canvas }]}
      edges={['top', 'left', 'right']}
    >
      <StatusBar
        barStyle={colorScheme === 'dark' ? 'light-content' : 'dark-content'}
      />
      <View
        style={[
          styles.navigation,
          { borderBottomColor: colors.border, flexDirection: direction },
        ]}
      >
        <View style={styles.navBrand}>
          <GalleryText style={[styles.eyebrow, { color: colors.primary }]}>
            TOKEN GALLERY
          </GalleryText>
          <GalleryText style={[styles.navTitle, { color: colors.primaryText }]}>
            Financial wellbeing
          </GalleryText>
        </View>
        <IconAction
          label="Open token details"
          symbol="i"
          color={colors.primary}
          onPress={() => setModalVisible(true)}
        />
      </View>

      {activeTab === 'Plan' ? (
        <ProductFlow />
      ) : (
        <ScrollView
          contentContainerStyle={[
            styles.scrollContent,
            mode === 'expanded' && styles.expandedScroll,
          ]}
        >
          <Animated.View
            style={{
              opacity: entrance,
              transform: [
                {
                  translateY: entrance.interpolate({
                    inputRange: [0, 1],
                    outputRange: [motion.distance, 0],
                  }),
                },
              ],
            }}
          >
            <View
              style={[
                styles.hero,
                { backgroundColor: colors.card, borderColor: colors.border },
              ]}
            >
              <GalleryText
                style={[
                  styles.heroTitle,
                  { color: colors.primaryText, textAlign },
                ]}
              >
                Native, accessible financial UI
              </GalleryText>
              <GalleryText
                style={[
                  styles.heroCopy,
                  { color: colors.secondaryText, textAlign },
                ]}
              >
                A touch-first reference of the canonical mobile token system for
                iOS and Android.
              </GalleryText>
              <View style={[styles.heroTags, { flexDirection: direction }]}>
                <GalleryText
                  style={[
                    styles.tag,
                    {
                      backgroundColor: colors.selected,
                      color: colors.primaryText,
                    },
                  ]}
                >
                  RTL-ready
                </GalleryText>
                <GalleryText
                  style={[
                    styles.tag,
                    {
                      backgroundColor: colors.selected,
                      color: colors.primaryText,
                    },
                  ]}
                >
                  2× type
                </GalleryText>
                <GalleryText
                  style={[
                    styles.tag,
                    {
                      backgroundColor: colors.selected,
                      color: colors.primaryText,
                    },
                  ]}
                >
                  Reduce motion
                </GalleryText>
              </View>
            </View>

            <Section title="Scale swatches" color={colors.primaryText}>
              <View style={[styles.swatches, { flexDirection: direction }]}>
                {[
                  ['Action', colors.primary],
                  ['Canvas', colors.canvas],
                  ['Selected', colors.selected],
                  ['Border', colors.border],
                ].map(([name, color]) => (
                  <View key={name} style={styles.swatch}>
                    <View
                      style={[
                        styles.swatchColor,
                        { backgroundColor: color, borderColor: colors.border },
                      ]}
                    />
                    <GalleryText style={{ color: colors.secondaryText }}>
                      {name}
                    </GalleryText>
                  </View>
                ))}
              </View>
              <View style={[styles.scaleRow, { flexDirection: direction }]}>
                {[0, 2, 4, 8, 12, 16, 20, 24, 32, 40, 48, 64].map(space => (
                  <View key={space} style={styles.spaceToken}>
                    <View
                      style={[
                        styles.spaceBar,
                        {
                          width: Math.max(2, Math.min(space, 48)),
                          backgroundColor: colors.primary,
                        },
                      ]}
                    />
                    <GalleryText style={{ color: colors.secondaryText }}>
                      {space}
                    </GalleryText>
                  </View>
                ))}
              </View>
            </Section>

            <Section title="Buttons and fields" color={colors.primaryText}>
              <View
                style={[
                  styles.componentCard,
                  { backgroundColor: colors.card, borderColor: colors.border },
                ]}
              >
                <View style={[styles.actionRow, { flexDirection: direction }]}>
                  <Action
                    label="Primary button"
                    onPress={() => setNoticeVisible(true)}
                    background={colors.primary}
                    color={colors.onPrimary}
                  />
                  <Action
                    label="Secondary"
                    onPress={hideNotice}
                    background={colors.selected}
                    color={colors.primaryText}
                    outlined
                  />
                  <IconAction
                    label="Save wellbeing plan"
                    symbol="♡"
                    color={colors.primary}
                    onPress={() => setNoticeVisible(true)}
                  />
                </View>
                <GalleryText
                  style={[styles.fieldLabel, { color: colors.primaryText }]}
                >
                  Text field
                </GalleryText>
                <TextInput
                  accessibilityLabel="Savings goal"
                  value={query}
                  onChangeText={setQuery}
                  allowFontScaling
                  maxFontSizeMultiplier={2}
                  placeholder="Name your goal"
                  placeholderTextColor={colors.secondaryText}
                  style={[
                    styles.textField,
                    {
                      color: colors.primaryText,
                      borderColor: colors.border,
                      textAlign,
                    },
                  ]}
                />
                {noticeVisible && (
                  <GalleryText
                    accessibilityLiveRegion="polite"
                    style={{ color: colors.secondaryText }}
                  >
                    Press feedback, entrance, and exit use native Animated with{' '}
                    {reduceMotion ? 'zero' : motion.duration}ms motion.
                  </GalleryText>
                )}
              </View>
            </Section>

            <View
              style={[
                styles.responsiveColumns,
                mode === 'compact' && styles.compactColumn,
              ]}
            >
              <View style={styles.column}>
                <Section title="Cards" color={colors.primaryText}>
                  <View
                    style={[
                      styles.componentCard,
                      {
                        backgroundColor: colors.card,
                        borderColor: colors.border,
                      },
                    ]}
                  >
                    <GalleryText style={{ color: colors.secondaryText }}>
                      Available to save
                    </GalleryText>
                    <GalleryText
                      style={[styles.balance, { color: colors.primaryText }]}
                    >
                      $1,284.50
                    </GalleryText>
                    <View
                      style={[
                        styles.progressTrack,
                        { backgroundColor: colors.selected },
                      ]}
                    >
                      <View
                        style={[
                          styles.progressValue,
                          { backgroundColor: colors.primary },
                        ]}
                      />
                    </View>
                    <GalleryText style={{ color: colors.secondaryText }}>
                      64% of your June target
                    </GalleryText>
                  </View>
                </Section>
              </View>
              <View style={styles.column}>
                <Section title="List rows" color={colors.primaryText}>
                  <View
                    style={[
                      styles.componentCard,
                      {
                        backgroundColor: colors.card,
                        borderColor: colors.border,
                      },
                    ]}
                  >
                    {[
                      'Paycheck · Friday',
                      'Groceries · This week',
                      'Emergency fund · Goal',
                    ].map((item, index) => (
                      <Pressable
                        key={item}
                        accessibilityRole="button"
                        accessibilityLabel={item}
                        style={({ pressed }) => [
                          styles.listRow,
                          {
                            borderBottomColor: colors.border,
                            opacity: pressed ? 0.86 : 1,
                            flexDirection: direction,
                          },
                        ]}
                      >
                        <View style={styles.listText}>
                          <GalleryText style={{ color: colors.primaryText }}>
                            {item}
                          </GalleryText>
                          <GalleryText style={{ color: colors.secondaryText }}>
                            {index === 0
                              ? '+ $2,480'
                              : index === 1
                              ? '− $186'
                              : '$1,284 saved'}
                          </GalleryText>
                        </View>
                        <GalleryText style={{ color: colors.primary }}>
                          ›
                        </GalleryText>
                      </Pressable>
                    ))}
                  </View>
                </Section>
              </View>
            </View>

            <Section
              title="Loading, empty, and error"
              color={colors.primaryText}
            >
              <View
                style={[styles.stateControls, { flexDirection: direction }]}
              >
                <Action
                  label="Loading"
                  accessibilityLabel="Show loading state"
                  onPress={() => setState('loading')}
                  background={colors.selected}
                  color={colors.primaryText}
                />
                <Action
                  label="Empty"
                  accessibilityLabel="Show empty state"
                  onPress={() => setState('empty')}
                  background={colors.selected}
                  color={colors.primaryText}
                />
                <Action
                  label="Error"
                  accessibilityLabel="Show error state"
                  onPress={() => setState('error')}
                  background={colors.selected}
                  color={colors.primaryText}
                />
                <Action
                  label="Ready"
                  accessibilityLabel="Show ready state"
                  onPress={() => setState('ready')}
                  background={colors.primary}
                  color={colors.onPrimary}
                />
              </View>
              <View
                style={[
                  styles.componentCard,
                  { backgroundColor: colors.card, borderColor: colors.border },
                ]}
              >
                <StatePreview
                  state={state}
                  onRetry={() => setState('ready')}
                  t={t}
                />
              </View>
            </Section>

            <Section title="All token values" color={colors.primaryText}>
              <GalleryText style={{ color: colors.secondaryText }}>
                All {tokenEntries.length} resolved tokens in the {profile}{' '}
                profile.
              </GalleryText>
              <View style={[styles.tokenTable, { borderColor: colors.border }]}>
                {tokenEntries.map(([path, value]) => (
                  <View
                    key={path}
                    style={[
                      styles.tokenRow,
                      {
                        borderBottomColor: colors.border,
                        flexDirection: direction,
                      },
                    ]}
                  >
                    <GalleryText
                      style={[
                        styles.tokenPath,
                        { color: colors.primaryText, textAlign },
                      ]}
                    >
                      {path}
                    </GalleryText>
                    <GalleryText
                      style={[
                        styles.tokenValue,
                        { color: colors.secondaryText, textAlign },
                      ]}
                    >
                      {typeof value === 'object'
                        ? JSON.stringify(value)
                        : String(value)}
                    </GalleryText>
                  </View>
                ))}
              </View>
            </Section>

            <Section title="Accessibility stress" color={colors.primaryText}>
              <View
                style={[
                  styles.componentCard,
                  { backgroundColor: colors.card, borderColor: colors.border },
                ]}
              >
                <GalleryText
                  style={[
                    styles.stressTitle,
                    { color: colors.primaryText, textAlign },
                  ]}
                >
                  A long savings goal title wraps before any action is clipped
                  at the largest supported text size.
                </GalleryText>
                <GalleryText
                  style={[
                    styles.stressCopy,
                    { color: colors.secondaryText, textAlign },
                  ]}
                >
                  Directional layout is logical for Arabic and Hebrew, status
                  uses symbols plus words, and every control keeps a native role
                  and label.
                </GalleryText>
              </View>
            </Section>
          </Animated.View>
        </ScrollView>
      )}

      <View
        accessibilityLabel="Navigation"
        style={[
          styles.tabBar,
          {
            backgroundColor: colors.card,
            borderTopColor: colors.border,
            flexDirection: direction,
          },
        ]}
      >
        {['Overview', 'Plan', 'Gallery', 'Settings'].map(tab => (
          <Pressable
            key={tab}
            accessibilityRole="tab"
            accessibilityState={{ selected: activeTab === tab }}
            accessibilityLabel={`${tab} navigation tab`}
            onPress={() => setActiveTab(tab)}
            style={({ pressed }) => [
              styles.tab,
              { opacity: pressed ? 0.86 : 1 },
            ]}
          >
            <GalleryText
              style={{
                color:
                  activeTab === tab ? colors.primary : colors.secondaryText,
              }}
            >
              {tab}
            </GalleryText>
          </Pressable>
        ))}
      </View>

      <Modal
        visible={modalVisible}
        transparent
        animationType={reduceMotion ? 'none' : 'fade'}
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={styles.modalScrim}>
          <View
            accessibilityViewIsModal
            style={[
              styles.modalCard,
              { backgroundColor: colors.card, borderColor: colors.border },
            ]}
          >
            <View style={[styles.modalHeader, { flexDirection: direction }]}>
              <GalleryText
                style={[styles.sectionTitle, { color: colors.primaryText }]}
              >
                Token details
              </GalleryText>
              <IconAction
                label="Dismiss token details"
                symbol="×"
                color={colors.primary}
                onPress={() => setModalVisible(false)}
              />
            </View>
            <GalleryText style={{ color: colors.secondaryText }}>
              This gallery resolves the canonical financial-wellbeing DTCG asset
              through generated tokens.ts and theme.ts. Platform profiles
              preserve 44pt iOS and 48dp Android touch targets.
            </GalleryText>
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
}

export default function App() {
  return (
    <SafeAreaProvider>
      <AppContent />
    </SafeAreaProvider>
  );
}

const toneStyles = StyleSheet.create({
  primary: {},
  secondary: {},
  inverse: { color: '#FFFFFF' },
});

const styles = StyleSheet.create({
  safeArea: { flex: 1 },
  text: {
    fontFamily: Platform.select({ ios: 'System', android: 'sans-serif' }),
    fontSize: 16,
    lineHeight: 23,
  },
  navigation: {
    minHeight: 64,
    paddingHorizontal: 16,
    paddingVertical: 10,
    justifyContent: 'space-between',
    alignItems: 'center',
    borderBottomWidth: StyleSheet.hairlineWidth,
  },
  navBrand: { flexShrink: 1 },
  eyebrow: { fontSize: 12, fontWeight: '800', letterSpacing: 1.1 },
  navTitle: { fontSize: 21, lineHeight: 26, fontWeight: '800' },
  iconAction: {
    width: 48,
    minHeight: 48,
    borderWidth: 1,
    borderRadius: 24,
    alignItems: 'center',
    justifyContent: 'center',
  },
  icon: { fontSize: 22, fontWeight: '800' },
  scrollContent: {
    width: '100%',
    alignSelf: 'center',
    padding: 16,
    paddingBottom: 104,
  },
  expandedScroll: { maxWidth: 960 },
  hero: { borderWidth: 1, borderRadius: 20, padding: 20, gap: 10 },
  heroTitle: { fontSize: 28, lineHeight: 35, fontWeight: '800' },
  heroCopy: { fontSize: 17, lineHeight: 25 },
  heroTags: { flexWrap: 'wrap', gap: 8, marginTop: 4 },
  tag: {
    overflow: 'hidden',
    borderRadius: 999,
    paddingHorizontal: 10,
    paddingVertical: 5,
    fontSize: 13,
    fontWeight: '700',
  },
  section: { marginTop: 28, gap: 12 },
  sectionTitle: { fontSize: 20, lineHeight: 27, fontWeight: '800' },
  swatches: { flexWrap: 'wrap', gap: 12 },
  swatch: { width: 72, gap: 5 },
  swatchColor: { height: 44, borderRadius: 12, borderWidth: 1 },
  scaleRow: { flexWrap: 'wrap', gap: 10, alignItems: 'flex-end' },
  spaceToken: { gap: 4, minWidth: 26 },
  spaceBar: { height: 8, borderRadius: 4 },
  componentCard: { borderWidth: 1, borderRadius: 20, padding: 16, gap: 12 },
  actionRow: { alignItems: 'center', flexWrap: 'wrap', gap: 10 },
  action: {
    minHeight: 48,
    paddingHorizontal: 20,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  actionText: { fontWeight: '700' },
  actionOutlined: { borderWidth: 1, borderColor: '#738078' },
  fieldLabel: { fontSize: 15, lineHeight: 20, fontWeight: '700', marginTop: 8 },
  textField: {
    minHeight: 52,
    borderWidth: 1,
    borderRadius: 12,
    paddingHorizontal: 14,
    fontSize: 17,
  },
  responsiveColumns: { flexDirection: 'row', gap: 16 },
  compactColumn: { flexDirection: 'column' },
  column: { flex: 1, minWidth: 0 },
  balance: { fontSize: 32, lineHeight: 40, fontWeight: '800' },
  progressTrack: { height: 12, overflow: 'hidden', borderRadius: 6 },
  progressValue: { width: '64%', height: '100%', borderRadius: 6 },
  listRow: {
    minHeight: 56,
    alignItems: 'center',
    justifyContent: 'space-between',
    borderBottomWidth: StyleSheet.hairlineWidth,
    gap: 12,
  },
  listText: { flex: 1, gap: 2 },
  stateControls: { flexWrap: 'wrap', gap: 8 },
  statePreview: {
    minHeight: 150,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    padding: 12,
  },
  stateIcon: { fontSize: 38, lineHeight: 44, fontWeight: '800' },
  stateTitle: {
    fontSize: 18,
    lineHeight: 25,
    fontWeight: '800',
    textAlign: 'center',
  },
  tokenTable: {
    borderTopWidth: StyleSheet.hairlineWidth,
    borderLeftWidth: StyleSheet.hairlineWidth,
    borderRightWidth: StyleSheet.hairlineWidth,
    borderRadius: 12,
    overflow: 'hidden',
  },
  tokenRow: {
    justifyContent: 'space-between',
    gap: 12,
    padding: 10,
    borderBottomWidth: StyleSheet.hairlineWidth,
  },
  tokenPath: { flex: 1, fontSize: 13, lineHeight: 18, fontWeight: '700' },
  tokenValue: { flex: 1, fontSize: 12, lineHeight: 17 },
  stressTitle: { fontSize: 24, lineHeight: 33, fontWeight: '800' },
  stressCopy: { fontSize: 19, lineHeight: 28 },
  tabBar: {
    minHeight: 64,
    borderTopWidth: StyleSheet.hairlineWidth,
    justifyContent: 'space-around',
    alignItems: 'stretch',
  },
  tab: {
    flex: 1,
    minHeight: 56,
    paddingHorizontal: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  modalScrim: {
    flex: 1,
    justifyContent: 'flex-end',
    backgroundColor: 'rgba(16, 35, 26, 0.48)',
  },
  modalCard: {
    borderTopLeftRadius: 28,
    borderTopRightRadius: 28,
    borderWidth: 1,
    padding: 24,
    gap: 16,
  },
  modalHeader: {
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: 12,
  },
});
