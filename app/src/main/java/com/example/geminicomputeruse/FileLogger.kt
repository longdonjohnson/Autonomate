package com.example.geminicomputeruse

import android.content.Context
import android.os.Environment
import java.io.File
import java.io.FileWriter
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class FileLogger(private val context: Context) {

    private val logFile: File by lazy {
        val path = context.getExternalFilesDir(null)
        File(path, "logs.txt")
    }

    fun log(message: String) {
        try {
            val timestamp = SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS", Locale.getDefault()).format(Date())
            FileWriter(logFile, true).use {
                it.append("$timestamp: $message\n")
            }
        } catch (e: Exception) {
            // Handle exceptions, e.g., if storage is not available
        }
    }
}