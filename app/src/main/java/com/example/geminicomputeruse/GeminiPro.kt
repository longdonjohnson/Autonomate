package com.example.geminicomputeruse

import android.graphics.Bitmap
import com.google.ai.client.generativeai.GenerativeModel
import com.google.ai.client.generativeai.type.content

object GeminiPro {

    suspend fun getResponse(apiKey: String, prompt: String, image: Bitmap): String {
        val generativeModel = GenerativeModel(
            modelName = "gemini-2.5-computer-use-preview-10-2025",
            apiKey = apiKey
        )

        val inputContent = content {
            image(image)
            text(prompt)
        }

        val response = generativeModel.generateContent(inputContent)
        return response.text ?: "Error: Could not get a response from the model."
    }
}