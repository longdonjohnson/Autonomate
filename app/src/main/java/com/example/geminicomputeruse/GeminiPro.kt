package com.example.geminicomputeruse

import android.graphics.Bitmap
import com.google.ai.client.generativeai.GenerativeModel
import com.google.ai.client.generativeai.type.content
import com.google.ai.client.generativeai.type.generationConfig

object GeminiPro {

    suspend fun getResponse(apiKey: String, prompt: String, image: Bitmap): String {
        val config = generationConfig {
            temperature = 0.7f
        }

        val generativeModel = GenerativeModel(
            modelName = "gemini-2.5-computer-use-preview-10-2025",
            apiKey = apiKey,
            generationConfig = config
        )

        val inputContent = content {
            image(image)
            text(prompt)
        }

        val response = generativeModel.generateContent(inputContent)
        return response.text ?: "Error: Could not get a response from the model."
    }
}