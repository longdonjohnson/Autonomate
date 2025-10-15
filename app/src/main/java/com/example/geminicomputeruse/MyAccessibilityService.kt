package com.example.geminicomputeruse

import android.accessibilityservice.AccessibilityService
import android.view.accessibility.AccessibilityNodeInfo
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.os.Bundle
import android.view.accessibility.AccessibilityEvent
import androidx.localbroadcastmanager.content.LocalBroadcastManager
import com.google.gson.Gson
import com.google.gson.JsonSyntaxException

class MyAccessibilityService : AccessibilityService() {

    companion object {
        const val ACTION_PERFORM_ACTION = "com.example.geminicomputeruse.PERFORM_ACTION"
        const val EXTRA_ACTION_COMMAND = "extra_action_command"
    }

    private val gson = Gson()

    private val actionReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            if (intent?.action == ACTION_PERFORM_ACTION) {
                val command = intent.getStringExtra(EXTRA_ACTION_COMMAND)
                if (command != null) {
                    processCommand(command)
                }
            }
        }
    }

    override fun onServiceConnected() {
        super.onServiceConnected()
        val filter = IntentFilter(ACTION_PERFORM_ACTION)
        LocalBroadcastManager.getInstance(this).registerReceiver(actionReceiver, filter)
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        // Not needed for now
    }

    private fun processCommand(command: String) {
        try {
            val actionData = gson.fromJson(command, ActionData::class.java)
            val rootNode = rootInActiveWindow ?: return
            val targetNode = findNodeByText(rootNode, actionData.target)

            when (actionData.action.lowercase()) {
                "click" -> targetNode?.performAction(AccessibilityNodeInfo.ACTION_CLICK)
                "type" -> {
                    val arguments = Bundle()
                    arguments.putCharSequence(
                        AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE,
                        actionData.text
                    )
                    targetNode?.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, arguments)
                }
                "scroll" -> {
                    val scrollDirection = if (actionData.direction?.lowercase() == "up") {
                        AccessibilityNodeInfo.ACTION_SCROLL_BACKWARD
                    } else {
                        AccessibilityNodeInfo.ACTION_SCROLL_FORWARD
                    }
                    targetNode?.performAction(scrollDirection)
                }
            }
            rootNode.recycle()
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
        // Not needed for now
    }

    override fun onDestroy() {
        super.onDestroy()
        LocalBroadcastManager.getInstance(this).unregisterReceiver(actionReceiver)
    }

    data class ActionData(
        val action: String,
        val target: String,
        val text: String? = null,
        val direction: String? = null
    )
}