package com.example.geminicomputeruse

import android.graphics.Bitmap
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

class MainViewModel : ViewModel() {

    private val _response = MutableLiveData<String>()
    val response: LiveData<String> = _response

    private val _error = MutableLiveData<String>()
    val error: LiveData<String> = _error

    fun getResponse(apiKey: String, prompt: String, image: Bitmap) {
        viewModelScope.launch(Dispatchers.IO) {
            try {
                val result = GeminiPro.getResponse(apiKey, prompt, image)
                _response.postValue(result)
            } catch (e: Exception) {
                _error.postValue(e.message)
            }
        }
    }
}