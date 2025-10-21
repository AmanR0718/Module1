import 'dotenv/config';

export default {
  expo: {
    name: "Zambian Farmer System",
    slug: "zambian-farmer-mobile",
    version: "1.0.0",
    orientation: "portrait",
    icon: "./assets/icon.png",
    userInterfaceStyle: "light",
    splash: {
      image: "./assets/splash.png",
      resizeMode: "contain",
      backgroundColor: "#198A48",
    },
    assetBundlePatterns: ["**/*"],
    ios: {
      supportsTablet: true,
      bundleIdentifier: "com.zambia.farmerapp",
    },
    android: {
      adaptiveIcon: {
        foregroundImage: "./assets/adaptive-icon.png",
        backgroundColor: "#198A48",
      },
      permissions: [
        "ACCESS_FINE_LOCATION",
        "ACCESS_COARSE_LOCATION",
        "CAMERA",
        "READ_EXTERNAL_STORAGE",
        "WRITE_EXTERNAL_STORAGE",
      ],
      package: "com.zambia.farmerapp",
    },
    web: {
      favicon: "./assets/favicon.png",
    },
    plugins: [
      [
        "expo-camera",
        {
          cameraPermission:
            "Allow app to access camera for document scanning and barcode scanning.",
        },
      ],
      [
        "expo-location",
        {
          locationAlwaysAndWhenInUsePermission:
            "Allow app to use your location for farmer registration.",
        },
      ],
      "expo-sqlite",
      "expo-secure-store", // ✅ Added here
    ],
    extra: {
      apiUrl:
        "https://laughing-chainsaw-p54vpq5x945276p5-8000.app.github.dev",
      eas: {
        projectId: "11a726c3-1588-4c2d-92b7-7f2a626e1916",
      },
    },
    platforms: ["ios", "android", "web"],
  },
};
