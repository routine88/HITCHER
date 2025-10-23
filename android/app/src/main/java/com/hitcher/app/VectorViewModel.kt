package com.hitcher.app

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

class VectorViewModel : ViewModel() {

    private val _vectorUiState = MutableLiveData(VectorUiState())
    val vectorUiState: LiveData<VectorUiState> = _vectorUiState

    private val repository = VectorRepository()

    fun loadVectors() {
        viewModelScope.launch(Dispatchers.IO) {
            _vectorUiState.postValue(
                VectorUiState(
                    statusMessage = "Loading Hitcher vectors…",
                    isLoading = true
                )
            )
            val result = repository.fetchVectorSummary()
            _vectorUiState.postValue(result)
        }
    }
}
