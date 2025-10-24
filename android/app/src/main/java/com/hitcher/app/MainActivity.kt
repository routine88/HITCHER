package com.hitcher.app

import android.os.Bundle
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.Observer
import com.hitcher.app.databinding.ActivityMainBinding

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private val viewModel: VectorViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupObservers()
        setupInteractions()
        viewModel.loadVectors()
    }

    private fun setupObservers() {
        viewModel.vectorUiState.observe(this, Observer { state ->
            binding.statusText.text = state.statusMessage
            binding.vectorCount.text = getString(R.string.vector_count, state.availableVectors)
            binding.refreshButton.isEnabled = !state.isLoading
        })
    }

    private fun setupInteractions() {
        binding.refreshButton.setOnClickListener {
            viewModel.loadVectors()
        }
    }
}
