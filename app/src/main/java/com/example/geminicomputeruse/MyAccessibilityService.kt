package com.example.geminicomputeruse

import android.accessibilityservice.AccessibilityService
import android.os.Bundle
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo
import com.google.gson.Gson
import com.google.gson.JsonSyntaxException
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.launch

class MyAccessibilityService : AccessibilityService() {

    private val gson = Gson()
    private val serviceJob = SupervisorJob()
    private val serviceScope = CoroutineScope(Dispatchers.Main + serviceJob)

    override fun onServiceConnected() {
        super.onServiceConnected()
        FileLogger.log("MyAccessibilityService", "Service connected")
        serviceScope.launch {
            AccessibilityCommandBus.commands.collectLatest { command ->
                FileLogger.log("MyAccessibilityService", "Command received: $command")
                processCommand(command)
            }
        }
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        // Not needed for now
    }

    private fun processCommand(command: String) {
        FileLogger.log("MyAccessibilityService", "Processing command: $command")
        try {
            val actionData = gson.fromJson(command, ActionData::class.java)
            val rootNode = rootInActiveWindow ?: return
            val targetNode = findNodeByText(rootNode, actionData.target)

            if (targetNode == null) {
                FileLogger.log("MyAccessibilityService", "Target node not found for target: ${actionData.target}")
                return
            }

            FileLogger.log("MyAccessibilityService", "Performing action '${actionData.action}' on target: ${actionData.target}")
            when (actionData.action.lowercase()) {
                "click" -> targetNode.performAction(AccessibilityNodeInfo.ACTION_CLICK)
                "type" -> {
                    val arguments = Bundle()
                    arguments.putCharSequence(
                        AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE,
                        actionData.text
                    )
                    targetNode.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, arguments)
                }
                "scroll" -> {
                    val scrollDirection = if (actionData.direction?.lowercase() == "up") {
                        AccessibilityNodeInfo.ACTION_SCROLL_BACKWARD
                    } else {
                        AccessibilityNodeInfo.ACTION_SCROLL_FORWARD
                    }
                    targetNode.performAction(scrollDirection)
                }
            }
        } catch (e: JsonSyntaxException) {
            // Handle cases where the command is not valid JSON
        }
    }

    private fun findNodeByText(rootNode: AccessibilityNodeInfo, text: String): AccessibilityNodeInfo? {
        // First, try to find an exact match
        var nodes = rootNode.findAccessibilityNodeInfosByText(text)
        for (node in nodes) {
            if (node.text?.toString().equals(text, ignoreCase = true) ||
                node.contentDescription?.toString().equals(text, ignoreCase = true)
            ) {
                return node
            }
        }

        // If no exact match, try to find a partial match
        nodes = rootNode.findAccessibilityNodeInfosByText(text)
        for (node in nodes) {
            if (node.text?.toString()?.contains(text, ignoreCase = true) == true ||
                node.contentDescription?.toString()?.contains(text, ignoreCase = true) == true
            ) {
                return node
            }
        }
        return null
    }

    override fun onInterrupt() {
        serviceJob.cancel()
    }

    override fun onDestroy() {
        super.onDestroy()
        serviceJob.cancel()
    }

    data class ActionData(
        val action: String,
        val target: String,
        val text: String? = null,
        val direction: String? = null
    )
}