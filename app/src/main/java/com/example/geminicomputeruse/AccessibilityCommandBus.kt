package com.example.geminicomputeruse

import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.asSharedFlow

object AccessibilityCommandBus {

    private val _commands = MutableSharedFlow<String>()
    val commands = _commands.asSharedFlow()

    suspend fun sendCommand(command: String) {
        _commands.emit(command)
    }
}