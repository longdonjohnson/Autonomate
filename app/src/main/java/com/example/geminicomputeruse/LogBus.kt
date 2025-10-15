package com.example.geminicomputeruse

import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.asSharedFlow

/**
 * A simple event bus for logging messages to the UI.
 */
object LogBus {

    private val _logs = MutableSharedFlow<String>()
    val logs = _logs.asSharedFlow()

    suspend fun log(message: String) {
        _logs.emit(message)
    }
}