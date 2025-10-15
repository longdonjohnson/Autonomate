package com.example.geminicomputeruse

import android.graphics.Bitmap
import com.google.ai.client.generativeai.GenerativeModel
import com.google.ai.client.generativeai.type.content
import com.google.ai.client.generativeai.type.generationConfig

import android.util.Base64

object GeminiPro {

    suspend fun getResponse(apiKey: String, prompt: String, base64Image: String): String {
        val config = generationConfig {
            temperature = 0.7f
        }

        val generativeModel = GenerativeModel(
            // As of October 2025, "gemini-2.5-computer-use-preview-10-2025" is the correct model
            // for this use case, according to the Google AI documentation.
            modelName = "gemini-2.5-computer-use-preview-10-2025",
            apiKey = apiKey,
            generationConfig = config
        )

        val inputContent = content {
            text(prompt)
            // The image is sent as a base64 string. The model expects the image to be in PNG format.
            image(Base64.decode(base64Image, Base64.DEFAULT))
        }

        val response = generativeModel.generateContent(inputContent)
        return response.text ?: "Error: Could not get a response from the model."
    }
}