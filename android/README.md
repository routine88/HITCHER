# Hitcher Android Client

This module contains the native Android application for the Hitcher vector-sharing platform. The current milestone focuses on foundational scaffolding so the team can iterate on flows defined in the PRD.

## Highlights
- Kotlin-based project targeting Android API 24+ with Material theming.
- `MainActivity` renders an Explore placeholder with vector status messaging.
- MVVM architecture with `VectorViewModel`, repository abstraction, and coroutine-powered data fetch.
- Retrofit dependencies pre-configured for upcoming Hitcher API integration.
- Gradle wrapper and configuration aligned with Android Gradle Plugin 8.2.

## Local Development
1. Install Android Studio Hedgehog (or newer) with Android SDK 34.
2. Open the `android` directory in Android Studio.
3. Sync Gradle and allow dependencies to download.
4. Run the `app` configuration on an emulator or device.

## Next Steps
- Implement navigation scaffolding for Explore, My Trips, Messages, and Profile tabs.
- Hook `VectorRepository` into the FastAPI backend using Retrofit + Moshi models.
- Add authentication onboarding screens and persistence.
- Introduce UI tests using Espresso for the hook-up confirmation flow.
