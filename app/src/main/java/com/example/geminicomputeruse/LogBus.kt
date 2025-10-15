package com.example.geminicomputeruse

import android.content.Context
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.asSharedFlow

/**
 * A simple event bus for logging messages to the UI and a file.
 */
object LogBus {

    private lateinit var fileLogger: FileLogger

    private val _logs = MutableSharedFlow<String>()
    val logs = _logs.asSharedFlow()

    fun initialize(context: Context) {
        fileLogger = FileLogger(context)
    }

    suspend fun log(message: String) {
        fileLogger.log(message)
        _logs.emit(message)
    }
}