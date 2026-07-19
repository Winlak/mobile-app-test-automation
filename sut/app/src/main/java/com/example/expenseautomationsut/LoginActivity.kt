package com.example.expenseautomationsut

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

class LoginActivity : AppCompatActivity() {
    private lateinit var store: SessionStore

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        store = SessionStore(this)
        if (store.isLoggedIn()) {
            openExpenses()
            return
        }
        setContentView(R.layout.activity_login)

        val email = findViewById<EditText>(R.id.email)
        val password = findViewById<EditText>(R.id.password)
        val error = findViewById<TextView>(R.id.login_error)
        findViewById<Button>(R.id.login_button).setOnClickListener {
            error.visibility = View.GONE
            if (store.authenticate(email.text.toString().trim(), password.text.toString())) {
                openExpenses()
            } else {
                error.text = "Неверный e-mail или пароль"
                error.visibility = View.VISIBLE
            }
        }
    }

    private fun openExpenses() {
        startActivity(Intent(this, ExpensesActivity::class.java))
        finish()
    }
}
