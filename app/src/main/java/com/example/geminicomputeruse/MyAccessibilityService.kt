package com.example.geminicomputeruse

import android.accessibilityservice.AccessibilityService
import android.accessibilityservice.AccessibilityNodeInfo
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.view.accessibility.AccessibilityEvent
import androidx.localbroadcastmanager.content.LocalBroadcastManager

class MyAccessibilityService : AccessibilityService() {

    companion object {
        const val ACTION_PERFORM_ACTION = "com.example.geminicomputeruse.PERFORM_ACTION"
        const val EXTRA_ACTION_COMMAND = "extra_action_command"
    }

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
        val parts = command.split(":")
        if (parts.size == 2) {
            val action = parts[0].trim()
            val target = parts[1].trim().removeSurrounding("'")

            if (action.equals("click", ignoreCase = true)) {
                val rootNode = rootInActiveWindow
                if (rootNode != null) {
                    val targetNode = findNodeByText(rootNode, target)
                    targetNode?.performAction(AccessibilityNodeInfo.ACTION_CLICK)
                    rootNode.recycle()
                }
            }
        }
    }

    private fun findNodeByText(rootNode: AccessibilityNodeInfo, text: String): AccessibilityNodeInfo? {
        val nodes = rootNode.findAccessibilityNodeInfosByText(text)
        for (node in nodes) {
            if (node.text != null && node.text.toString().equals(text, ignoreCase = true)) {
                return node
            }
            if (node.contentDescription != null && node.contentDescription.toString().equals(text, ignoreCase = true)) {
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
}