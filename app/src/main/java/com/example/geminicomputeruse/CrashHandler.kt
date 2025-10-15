package com.example.geminicomputeruse

import android.content.Context
import java.io.PrintWriter
import java.io.StringWriter

class CrashHandler(private val context: Context) : Thread.UncaughtExceptionHandler {

    private val defaultHandler = Thread.getDefaultUncaughtExceptionHandler()

    override fun uncaughtException(thread: Thread, throwable: Throwable) {
        val stringWriter = StringWriter()
        throwable.printStackTrace(PrintWriter(stringWriter))
        val stackTrace = stringWriter.toString()

        val fileLogger = FileLogger(context)
        fileLogger.log("FATAL EXCEPTION: ${throwable.message}\n$stackTrace")

        defaultHandler?.uncaughtException(thread, throwable)
    }
}