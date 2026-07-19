package com.example.expenseautomationsut

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import java.math.BigDecimal

class ExpenseFormActivity : AppCompatActivity() {
    private lateinit var store: SessionStore
    private lateinit var titleInput: EditText
    private lateinit var amountInput: EditText
    private lateinit var categoryButton: Button
    private lateinit var error: TextView
    private var category = ExpensesActivity.CATEGORIES.first()
    private var original: Expense? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        store = SessionStore(this)
        if (!store.isLoggedIn()) {
            startActivity(Intent(this, LoginActivity::class.java))
            finish()
            return
        }
        setContentView(R.layout.activity_expense_form)
        titleInput = findViewById(R.id.expense_title)
        amountInput = findViewById(R.id.expense_amount)
        categoryButton = findViewById(R.id.category_button)
        error = findViewById(R.id.form_error)

        original = intent.getStringExtra(EXTRA_EXPENSE_ID)?.let(store::find)
        configureInitialState(original)
        categoryButton.setOnClickListener { showCategoryPicker() }
        findViewById<Button>(R.id.save_button).setOnClickListener { save() }
        findViewById<Button>(R.id.delete_button).setOnClickListener { confirmDelete() }
    }

    private fun configureInitialState(expense: Expense?) {
        findViewById<TextView>(R.id.form_title).text = if (expense == null) "Новый расход" else "Редактирование расхода"
        category = expense?.category ?: category
        categoryButton.text = category
        if (expense != null) {
            titleInput.setText(expense.title)
            amountInput.setText(expense.amount.toPlainString())
            findViewById<Button>(R.id.delete_button).visibility = View.VISIBLE
        }
    }

    private fun showCategoryPicker() {
        val current = ExpensesActivity.CATEGORIES.indexOf(category).coerceAtLeast(0)
        val dialog = AlertDialog.Builder(this)
            .setTitle("Категория")
            .setSingleChoiceItems(ExpensesActivity.CATEGORIES, current) { dialogInterface, selected ->
                category = ExpensesActivity.CATEGORIES[selected]
                categoryButton.text = category
                dialogInterface.dismiss()
            }
            .create()
        dialog.setOnShowListener {
            dialog.window?.decorView?.contentDescription = getString(R.string.category_dialog_desc)
        }
        dialog.show()
    }

    private fun save() {
        val title = titleInput.text.toString().trim()
        val amount = amountInput.text.toString().trim().replace(',', '.').toBigDecimalOrNull()
        when {
            title.isBlank() || amountInput.text.toString().trim().isBlank() -> showError("Заполните название и сумму")
            amount == null || amount <= BigDecimal.ZERO -> showError("Укажите сумму больше нуля")
            else -> {
                val expense = Expense(
                    id = original?.id ?: store.newId(),
                    title = title,
                    amount = amount,
                    category = category,
                )
                store.save(expense)
                finish()
            }
        }
    }

    private fun showError(message: String) {
        error.text = message
        error.visibility = View.VISIBLE
    }

    private fun confirmDelete() {
        val expense = original ?: return
        val dialog = AlertDialog.Builder(this)
            .setTitle("Удалить расход?")
            .setMessage("Это действие нельзя отменить")
            .setNegativeButton("Отмена", null)
            .setPositiveButton("Удалить") { _, _ ->
                store.delete(expense.id)
                finish()
            }
            .create()
        dialog.setOnShowListener {
            dialog.window?.decorView?.contentDescription = getString(R.string.confirmation_dialog_desc)
        }
        dialog.show()
    }

    companion object {
        private const val EXTRA_EXPENSE_ID = "expense_id"

        fun intent(context: Context, expenseId: String? = null): Intent =
            Intent(context, ExpenseFormActivity::class.java).apply {
                expenseId?.let { putExtra(EXTRA_EXPENSE_ID, it) }
            }
    }
}
