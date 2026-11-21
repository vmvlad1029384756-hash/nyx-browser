plugins {
    id("com.android.application")
}

android {
    namespace = "com.nyx.browser"
    compileSdk = 36

    defaultConfig {
        applicationId = "com.nyx.browser"
        minSdk = 26
        targetSdk = 36
        versionCode = 1
        versionName = "0.1.0-dev.1"
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }


    buildTypes {
        debug {
            applicationIdSuffix = ".debug"
            versionNameSuffix = "-debug"
        }
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}
