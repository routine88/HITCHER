package com.hitcher.app

data class VectorUiState(
    val statusMessage: String = "Preparing Hitcher",
    val availableVectors: Int = 0,
    val isLoading: Boolean = false
)
