package com.example.mouseonthegoprototype
import android.annotation.SuppressLint
import android.content.Context
import android.content.SharedPreferences
import kotlin.concurrent.thread
import android.view.LayoutInflater
import android.os.Bundle
import android.view.MotionEvent
import android.view.View
import android.widget.Button
import android.widget.CheckBox
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.Toast
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat

class MainActivity : AppCompatActivity() {
    private var serverIp = "192.168.94.110"
    private var serverPort = 12345
    private lateinit var sharedPreferences: SharedPreferences

    @SuppressLint("ClickableViewAccessibility")

    override fun onPause() {
        super.onPause()
        thread { sendSignalToServer("reset", serverIp, serverPort)}
    }

    override fun onStop() {
        super.onStop()
        thread { sendSignalToServer("reset", serverIp, serverPort)}
    }

    override fun onDestroy() {
        super.onDestroy()
        thread { sendSignalToServer("reset", serverIp, serverPort)}
    }

    @SuppressLint("ClickableViewAccessibility")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContentView(R.layout.activity_main)

        sharedPreferences = getSharedPreferences("app_settings", Context.MODE_PRIVATE)

        val savedIp = sharedPreferences.getString("server_ip", null)
        val savedPort = sharedPreferences.getInt("server_port", -1)

        if (savedIp != null && savedPort != -1) {
            serverIp = savedIp
            serverPort = savedPort
        } else {
            showInputDialog()
        }

        setUpMainWindow()
    }

    @SuppressLint("ClickableViewAccessibility")
    private fun setUpMainWindow() {
        setContentView(R.layout.activity_main)
        applyWindowInsets(findViewById(R.id.main))
        val openSettings: Button = findViewById(R.id.buttonSettings)
        openSettings.setOnClickListener {
            showInputDialog()
        }
        val checkBoxValue = sharedPreferences.getBoolean("checkBoxOption", false)
        if (checkBoxValue) {
            findViewById<Button>(R.id.buttonMouse4).visibility = View.VISIBLE
            findViewById<Button>(R.id.buttonMouse5).visibility = View.VISIBLE
        } else {
            findViewById<Button>(R.id.buttonMouse4).visibility = View.GONE
            findViewById<Button>(R.id.buttonMouse5).visibility = View.GONE
        }
        val buttonDirections = mapOf(
            R.id.buttonUp to "Up",
            R.id.buttonDown to "Down",
            R.id.buttonLeft to "Left",
            R.id.buttonRight to "Right",
            R.id.buttonLMB to "LMB",
            R.id.buttonRMB to "RMB",
            R.id.buttonMMB to "MMB",
            R.id.buttonScrollUp to "ScrollUp",
            R.id.buttonScrollDown to "ScrollDown",
            R.id.buttonMouse4 to "Mouse4",
            R.id.buttonMouse5 to "Mouse5",
        )
        findViewById<Button>(R.id.buttonReset).setOnClickListener {
            thread { sendSignalToServer("reset", serverIp, serverPort)}
        }
        buttonDirections.forEach { (buttonId, direction) ->
            val button: Button = findViewById(buttonId)
            button.setOnTouchListener { v, event ->
                when (event?.action) {
                    MotionEvent.ACTION_DOWN -> thread { sendSignalToServer("start_$direction", serverIp, serverPort) }
                    MotionEvent.ACTION_UP -> thread { sendSignalToServer("stop_$direction", serverIp, serverPort) }
                }
                v?.onTouchEvent(event) ?: true
            }
        }

        findViewById<Button>(R.id.buttonMacros).setOnClickListener {
            thread {
                try {
                    val macros_list = requestStringList(serverIp, serverPort)
                    runOnUiThread { setUpMacrosWindow(macros_list) }
                } catch (e: Exception) {
                    runOnUiThread {
                        Toast.makeText(
                            this,
                            "Не удалось получить список макросов.",
                            Toast.LENGTH_SHORT
                        ).show()
                    }
                }
            }
        }
    }

    private fun setUpMacrosWindow(macros_list: Array<String>) {
        setContentView(R.layout.macros_tab)
        applyWindowInsets(findViewById(R.id.main))
        setContentView(R.layout.macros_tab)
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main)) { v, insets ->
            val systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars())
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom)
            insets
        }
        val buttonContainer: LinearLayout = findViewById(R.id.buttonContainer)
        macros_list.forEach { text ->
            if (text != "") {
                val button = Button(this)
                button.text = text
                button.setOnClickListener {
                    thread {
                        sendSignalToServer("run_macro_$text", serverIp, serverPort)
                    }
                }
                buttonContainer.addView(button) // Add the button to the container
            }
        }
        findViewById<Button>(R.id.buttonToMain).setOnClickListener {
            setUpMainWindow()
        }
    }

    private fun applyWindowInsets(view: View) {
        ViewCompat.setOnApplyWindowInsetsListener(view) { v, insets ->
            val systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars())
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom)
            insets
        }
        ViewCompat.requestApplyInsets(view)
    }

    private fun showInputDialog() {
        val dialogView = LayoutInflater.from(this).inflate(R.layout.settings, null)
        val ipEditText = dialogView.findViewById<EditText>(R.id.editTextIpAddress)
        val portEditText = dialogView.findViewById<EditText>(R.id.editTextPort)
        val checkBox = dialogView.findViewById<CheckBox>(R.id.checkBoxOption)

        ipEditText.setText(sharedPreferences.getString("server_ip", serverIp))
        portEditText.setText(sharedPreferences.getInt("server_port", serverPort).toString())
        checkBox.isChecked = sharedPreferences.getBoolean("checkBoxOption", false)

        val dialogBuilder = AlertDialog.Builder(this)
            .setTitle("Меню настройки")
            .setMessage("Введите IPv4 адрес компьютера, который должен находится в той же локальной сети")
            .setView(dialogView)
            .setPositiveButton("Применить", null)  // Set to null to override default behavior
            .setNeutralButton("Проверка", null)    // Another button with a different action
            .setNegativeButton("Сбросить") { dialog, _ ->
                dialog.cancel()
            }

        val dialog = dialogBuilder.create()
        dialog.show()

        dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener {
            val userInput1 = ipEditText.text.toString()
            val userInput2 = portEditText.text.toString().toIntOrNull() ?: -1
            val checkBoxValue = checkBox.isChecked
            if (isValidIPv4(userInput1, userInput2)) {
                handleUserInput(userInput1, userInput2, checkBoxValue)  // Pass checkbox value
                dialog.dismiss()
            } else {
                Toast.makeText(this, "Некорректный формат IP или порта. Попробуйте снова.", Toast.LENGTH_SHORT).show()
            }
            if (checkBoxValue) {
                findViewById<Button>(R.id.buttonMouse4).visibility = View.VISIBLE
                findViewById<Button>(R.id.buttonMouse5).visibility = View.VISIBLE
            } else {
                findViewById<Button>(R.id.buttonMouse4).visibility = View.GONE
                findViewById<Button>(R.id.buttonMouse5).visibility = View.GONE
            }
        }

        dialog.getButton(AlertDialog.BUTTON_NEUTRAL).setOnClickListener {
            val userInput1 = ipEditText?.text.toString()
            val userInput2 = portEditText.text.toString().toIntOrNull() ?: -1
            if (isValidIPv4(userInput1, userInput2)) {
                thread {
                    val isConnected = isServerReachable(userInput1, userInput2)
                    runOnUiThread {
                        if (isConnected) Toast.makeText(this, "Соединение доступно", Toast.LENGTH_SHORT).show()
                        else Toast.makeText(this, "Не   удалось установить соединение", Toast.LENGTH_SHORT).show()
                    }
                }
            } else {
                Toast.makeText(this, "Некорректный формат IP или порта. Попробуйте снова.", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun isValidIPv4(ip: String, port: Int): Boolean {
        val ipv4Pattern = Regex(
            "^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}" +
                    "(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        )
        return ipv4Pattern.matches(ip) and (port > 0) and (port < 65535)
    }

    private fun handleUserInput(input1: String, input2: Int, checkBoxValue: Boolean) {
        Toast.makeText(this, "Valid IPv4 address: $input1 \n Valid port: $input2", Toast.LENGTH_SHORT).show()
        serverIp = input1
        serverPort = input2

        val editor = sharedPreferences.edit()
        editor.putString("server_ip", input1)
        editor.putInt("server_port", input2)
        editor.putBoolean("checkBoxOption", checkBoxValue)
        editor.apply()  // Apply the changes asynchronously
    }



}
