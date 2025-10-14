package com.example.geminicomputeruse

import android.graphics.Bitmap
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class MainActivity : AppCompatActivity() {

    private lateinit var actionButton: Button
    private lateinit var responseTextView: TextView
    // Per user instruction, the API key is hardcoded here for this project.
    // In a production app, this should be stored securely and not in source code.
    private val apiKey = "AIzaSyAk8PGkWMWtdpnmRZOCu-SRgWEaTrygCWQ"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        actionButton = findViewById(R.id.action_button)
        responseTextView = findViewById(R.id.response_textview)

        actionButton.setOnClickListener {
            lifecycleScope.launch(Dispatchers.IO) {
                // Observe: Create a dummy bitmap. In a real scenario, you'd capture the screen.
                val dummyBitmap = Bitmap.createBitmap(100, 100, Bitmap.Config.ARGB_8888)
                val prompt = "Click the 'Login' button."

                try {
                    val response = GeminiPro.getResponse(apiKey, prompt, dummyBitmap)
                    withContext(Dispatchers.Main) {
                        responseTextView.text = response
                    }
                } catch (e: Exception) {
                    withContext(Dispatchers.Main) {
                        responseTextView.text = "Error: ${e.message}"
                    }
                }
            }
        }
    }
}