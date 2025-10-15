package com.example.geminicomputeruse

import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.asSharedFlow

/**
 * A modern, coroutine-based event bus to send commands to the MyAccessibilityService.
 * This replaces the deprecated LocalBroadcastManager.
 */
object AccessibilityCommandBus {

    private val _commands = MutableSharedFlow<String>()
    val commands = _commands.asSharedFlow()

    suspend fun sendCommand(command: String) {
        _commands.emit(command)
    }
}