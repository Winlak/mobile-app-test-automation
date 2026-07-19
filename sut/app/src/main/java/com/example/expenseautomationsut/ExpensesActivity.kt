package com.example.expenseautomationsut

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView

class ExpensesActivity : AppCompatActivity() {
    private lateinit var store: SessionStore
    private lateinit var adapter: ExpenseAdapter
    private lateinit var filterButton: Button
    private lateinit var emptyState: TextView
    private var selectedCategory = ALL_CATEGORIES

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        store = SessionStore(this)
        if (!store.isLoggedIn()) {
            openLogin()
            return
        }
        setContentView(R.layout.activity_expenses)
        filterButton = findViewById(R.id.filter_button)
        emptyState = findViewById(R.id.empty_state)
        adapter = ExpenseAdapter { expense ->
            startActivity(ExpenseFormActivity.intent(this, expense.id))
        }
        findViewById<RecyclerView>(R.id.expense_list).apply {
            layoutManager = LinearLayoutManager(this@ExpensesActivity)
            adapter = this@ExpensesActivity.adapter
        }
        findViewById<Button>(R.id.add_button).setOnClickListener {
            startActivity(ExpenseFormActivity.intent(this))
        }
        findViewById<Button>(R.id.filter_button).setOnClickListener { showCategoryFilter() }
        findViewById<Button>(R.id.logout_button).setOnClickListener {
            store.logout()
            openLogin()
        }
    }

    override fun onResume() {
        super.onResume()
        if (::adapter.isInitialized) render()
    }

    private fun render() {
        val items = store.expenses().filter { selectedCategory == ALL_CATEGORIES || it.category == selectedCategory }
        adapter.submit(items)
        filterButton.text = selectedCategory
        emptyState.visibility = if (items.isEmpty()) View.VISIBLE else View.GONE
    }

    private fun showCategoryFilter() {
        val options = arrayOf(ALL_CATEGORIES, *CATEGORIES)
        val current = options.indexOf(selectedCategory).coerceAtLeast(0)
        val dialog = AlertDialog.Builder(this)
            .setTitle("Категория")
            .setSingleChoiceItems(options, current) { dialogInterface, selected ->
                selectedCategory = options[selected]
                dialogInterface.dismiss()
                render()
            }
            .create()
        dialog.setOnShowListener {
            dialog.window?.decorView?.contentDescription = getString(R.string.category_dialog_desc)
        }
        dialog.show()
    }

    private fun openLogin() {
        val intent = Intent(this, LoginActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        }
        startActivity(intent)
        finish()
    }

    companion object {
        const val ALL_CATEGORIES = "Все категории"
        val CATEGORIES = arrayOf("Продукты", "Транспорт", "Развлечения", "Здоровье")
    }
}
