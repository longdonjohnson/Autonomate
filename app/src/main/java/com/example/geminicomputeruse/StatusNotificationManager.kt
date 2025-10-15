package com.example.geminicomputeruse

import android.app.Notification
import android.app.NotificationManager
import android.content.Context
import androidx.core.app.NotificationCompat

class StatusNotificationManager(private val context: Context) {

    private val notificationManager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
    private val notificationId = 1

    fun show(status: String) {
        val notification = createNotification(status)
        notificationManager.notify(notificationId, notification)
    }

    fun update(status: String) {
        val notification = createNotification(status)
        notificationManager.notify(notificationId, notification)
    }

    fun dismiss() {
        notificationManager.cancel(notificationId)
    }

    private fun createNotification(status: String): Notification {
        return NotificationCompat.Builder(context, GeminiComputerUseApplication.STATUS_NOTIFICATION_CHANNEL_ID)
            .setContentTitle("Gemini Computer Use")
            .setContentText(status)
            .setSmallIcon(R.mipmap.ic_launcher) // Replace with a real icon
            .setOngoing(true)
            .build()
    }
}