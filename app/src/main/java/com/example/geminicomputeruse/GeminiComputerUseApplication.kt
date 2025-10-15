package com.example.geminicomputeruse

import android.app.Application
import android.app.NotificationChannel
import android.app.NotificationManager
import android.os.Build

class GeminiComputerUseApplication : Application() {

    companion object {
        const val STATUS_NOTIFICATION_CHANNEL_ID = "status_notification_channel"
    }

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
        LogBus.initialize(this)
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val name = "Status Notifications"
            val descriptionText = "Notifications that show the current status of the app"
            val importance = NotificationManager.IMPORTANCE_LOW
            val channel = NotificationChannel(STATUS_NOTIFICATION_CHANNEL_ID, name, importance).apply {
                description = descriptionText
            }
            // Register the channel with the system
            val notificationManager: NotificationManager =
                getSystemService(NOTIFICATION_SERVICE) as NotificationManager
            notificationManager.createNotificationChannel(channel)
        }
    }
}