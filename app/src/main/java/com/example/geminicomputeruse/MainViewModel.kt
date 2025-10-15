package com.example.geminicomputeruse

import android.app.Application
import android.graphics.Bitmap
import android.util.Log
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

class MainViewModel(application: Application) : AndroidViewModel(application) {

    private val statusNotificationManager = StatusNotificationManager(application)

    private val _error = MutableLiveData<String>()
    val error: LiveData<String> = _error

    fun getResponse(apiKey: String, prompt: String, image: Bitmap) {
        statusNotificationManager.show("Thinking...")
        viewModelScope.launch(Dispatchers.IO) {
            try {
                val result = GeminiPro.getResponse(apiKey, prompt, image)
                Log.d("MainViewModel", "Gemini Response: $result")
                AccessibilityCommandBus.sendCommand(result)
                statusNotificationManager.update("Action sent.")
            } catch (e: Exception) {
                Log.e("MainViewModel", "Error getting response from Gemini", e)
                _error.postValue(e.message)
                statusNotificationManager.update("Error: ${e.message}")
            }
        }
    }
}