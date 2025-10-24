package com.hitcher.app

import kotlinx.coroutines.delay

class VectorRepository {

    suspend fun fetchVectorSummary(): VectorUiState {
        // Placeholder for Retrofit call to Hitcher backend
        delay(300)
        return VectorUiState(
            statusMessage = "Connected to Hitcher backend",
            availableVectors = 0,
            isLoading = false
        )
    }
}
