package com.example.geminicomputeruse

import android.accessibilityservice.AccessibilityService
import android.view.accessibility.AccessibilityEvent

class MyAccessibilityService : AccessibilityService() {

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        // Not needed for now
    }

    override fun onInterrupt() {
        // Not needed for now
    }
}