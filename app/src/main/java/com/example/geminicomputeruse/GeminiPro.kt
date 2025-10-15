package com.example.geminicomputeruse

import android.graphics.Bitmap
import com.google.ai.client.generativeai.GenerativeModel
import com.google.ai.client.generativeai.type.content
import com.google.ai.client.generativeai.type.tool
import com.google.ai.client.generativeai.type.computeruse
import com.google.ai.client.generativeai.type.Environment

object GeminiPro {

    suspend fun getResponse(apiKey: String, prompt: String, image: Bitmap): String {
        val computerUseTool = tool {
            computeruse {
                environment = Environment.ENVIRONMENT_MOBILE
                excludedPredefinedFunctions = listOf(
                    "open_web_browser",
                    "search",
                    "navigate",
                    "hover_at",
                    "scroll_document",
                    "go_forward",
                    "key_combination",
                    "drag_and_drop"
                )
            }
        }

        val generativeModel = GenerativeModel(
            modelName = "gemini-2.5-computer-use-preview-10-2025",
            apiKey = apiKey,
            tools = listOf(computerUseTool)
        )

        val inputContent = content {
            image(image)
            text(prompt)
        }

        val response = generativeModel.generateContent(inputContent)
        return response.text ?: "Error: Could not get a response from the model."
    }
}