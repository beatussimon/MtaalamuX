import { ExpoConfig } from 'expo/config';

const config: ExpoConfig = {
  name: 'MtaalamuX',
  slug: 'mtx-mobile',
  scheme: 'mtx-mobile',
  version: '1.0.0',
  orientation: 'portrait',
  icon: './assets/icon.png',
  userInterfaceStyle: 'automatic',
  splash: {
    image: './assets/splash.png',
    resizeMode: 'contain',
    backgroundColor: '#ffffff',
  },
  assetBundlePatterns: ['**/*'],
  ios: {
    supportsTablet: true,
    bundleIdentifier: 'com.mtaalamux.mobile',
    buildNumber: '1',
    infoPlist: {
      NSCameraUsageDescription: 'MtaalamuX needs camera access to take photos.',
      NSPhotoLibraryUsageDescription: 'MtaalamuX needs photo library access.',
    },
    associatedDomains: ['applinks:mtaalamux.com'],
  },
  android: {
    adaptiveIcon: {
      foregroundImage: './assets/adaptive-icon.png',
      backgroundColor: '#ffffff',
    },
    package: 'com.mtaalamux.mobile',
    versionCode: 1,
    permissions: [
      'android.permission.CAMERA',
      'android.permission.READ_EXTERNAL_STORAGE',
      'android.permission.WRITE_EXTERNAL_STORAGE',
      'android.permission.POST_NOTIFICATIONS',
    ],
    intentFilters: [
      {
        action: 'VIEW',
        data: [
          {
            scheme: 'https',
            host: '*.mtaalamux.com',
            pathPrefix: '/chat',
          },
        ],
        category: ['BROWSABLE', 'DEFAULT'],
      },
    ],
  },
  web: {
    favicon: './assets/favicon.png',
    bundler: 'metro',
  },
  plugins: [
    'expo-router',
    ['expo-image-picker', {}],
    ['expo-notifications', { icon: './assets/notification-icon.png', color: '#0ea5e9' }],
  ],
  extra: {
    router: { origin: false },
    API_BASE_URL: process.env.API_BASE_URL || 'http://localhost:8000/api',
  },
  updates: {
    url: 'https://u.expo.dev/your-project-id',
    enabled: true,
  },
};

export default config;
