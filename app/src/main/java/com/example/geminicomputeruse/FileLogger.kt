package com.example.geminicomputeruse

import android.content.Context
import java.io.File
import java.io.FileWriter
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

object FileLogger {

    private lateinit var logFile: File

    fun initialize(context: Context) {
        val path = context.getExternalFilesDir(null)
        logFile = File(path, "logs.txt")
    }

    fun log(tag: String, message: String) {
        try {
            val timestamp = SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS", Locale.getDefault()).format(Date())
            FileWriter(logFile, true).use {
                it.append("$timestamp $tag: $message\n")
            }
        } catch (e: Exception) {
            // Handle exceptions
        }
    }
}