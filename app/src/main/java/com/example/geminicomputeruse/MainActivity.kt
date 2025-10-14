package com.example.geminicomputeruse

import android.app.Activity
import android.content.Context
import android.content.Intent
import android.graphics.Bitmap
import android.hardware.display.DisplayManager
import android.hardware.display.VirtualDisplay
import android.media.ImageReader
import android.media.projection.MediaProjection
import android.media.projection.MediaProjectionManager
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.util.DisplayMetrics
import android.provider.Settings
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.viewModels
import androidx.localbroadcastmanager.content.LocalBroadcastManager

class MainActivity : AppCompatActivity() {

    private lateinit var actionButton: Button
    private lateinit var responseTextView: TextView
    private lateinit var promptEditText: EditText
    private lateinit var enableAccessibilityButton: Button
    private val apiKey = BuildConfig.API_KEY

    private lateinit var mediaProjectionManager: MediaProjectionManager
    private var mediaProjection: MediaProjection? = null
    private var virtualDisplay: VirtualDisplay? = null
    private lateinit var imageReader: ImageReader

    private val viewModel: MainViewModel by viewModels()

    private val screenCaptureLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == Activity.RESULT_OK) {
            mediaProjection = mediaProjectionManager.getMediaProjection(result.resultCode, result.data!!)
            startScreenCapture()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        actionButton = findViewById(R.id.action_button)
        responseTextView = findViewById(R.id.response_textview)
        promptEditText = findViewById(R.id.prompt_edittext)
        enableAccessibilityButton = findViewById(R.id.enable_accessibility_button)

        mediaProjectionManager = getSystemService(Context.MEDIA_PROJECTION_SERVICE) as MediaProjectionManager

        actionButton.setOnClickListener {
            val captureIntent = mediaProjectionManager.createScreenCaptureIntent()
            screenCaptureLauncher.launch(captureIntent)
        }

        enableAccessibilityButton.setOnClickListener {
            val intent = Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)
            startActivity(intent)
        }

        viewModel.response.observe(this) { response ->
            responseTextView.text = response
            // Send the command to the accessibility service
            val intent = Intent(MyAccessibilityService.ACTION_PERFORM_ACTION)
            intent.putExtra(MyAccessibilityService.EXTRA_ACTION_COMMAND, response)
            LocalBroadcastManager.getInstance(this@MainActivity).sendBroadcast(intent)
            stopScreenCapture()
        }

        viewModel.error.observe(this) { error ->
            responseTextView.text = "Error: $error"
            stopScreenCapture()
        }
    }

    private fun startScreenCapture() {
        val displayMetrics = DisplayMetrics()
        windowManager.defaultDisplay.getMetrics(displayMetrics)
        val screenWidth = displayMetrics.widthPixels
        val screenHeight = displayMetrics.heightPixels

        imageReader = ImageReader.newInstance(screenWidth, screenHeight, android.graphics.PixelFormat.RGBA_8888, 2)
        virtualDisplay = mediaProjection?.createVirtualDisplay(
            "ScreenCapture",
            screenWidth,
            screenHeight,
            displayMetrics.densityDpi,
            DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR,
            imageReader.surface,
            null,
            null
        )

        // A short delay to allow the virtual display to be set up.
        // In a production app, a more robust solution would be needed to ensure the
        // screen is fully rendered before capturing.
        Handler(Looper.getMainLooper()).postDelayed({
            val image = imageReader.acquireLatestImage()
            if (image != null) {
                val planes = image.planes
                val buffer = planes[0].buffer
                val pixelStride = planes[0].pixelStride
                val rowStride = planes[0].rowStride
                val rowPadding = rowStride - pixelStride * screenWidth

                val bitmap = Bitmap.createBitmap(
                    screenWidth + rowPadding / pixelStride,
                    screenHeight,
                    Bitmap.Config.ARGB_8888
                )
                bitmap.copyPixelsFromBuffer(buffer)
                image.close()

                // Now we have the bitmap, let's call the Gemini API via the ViewModel
                val prompt = promptEditText.text.toString()
                viewModel.getResponse(apiKey, prompt, bitmap)
            }
        }, 1000)
    }

    private fun stopScreenCapture() {
        virtualDisplay?.release()
        imageReader.close()
        mediaProjection?.stop()
        mediaProjection = null
    }

    override fun onDestroy() {
        super.onDestroy()
        stopScreenCapture()
    }
}