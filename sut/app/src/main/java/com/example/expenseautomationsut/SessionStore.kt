package com.example.expenseautomationsut

import android.content.Context
import org.json.JSONArray
import java.util.UUID

class SessionStore(context: Context) {
    private val preferences = context.getSharedPreferences(PREFERENCES, Context.MODE_PRIVATE)

    fun authenticate(email: String, password: String): Boolean {
        val valid = email == DEMO_EMAIL && password == DEMO_PASSWORD
        if (valid) preferences.edit().putBoolean(KEY_LOGGED_IN, true).apply()
        return valid
    }

    fun isLoggedIn(): Boolean = preferences.getBoolean(KEY_LOGGED_IN, false)

    fun logout() {
        preferences.edit().putBoolean(KEY_LOGGED_IN, false).apply()
    }

    fun expenses(): List<Expense> {
        val source = preferences.getString(KEY_EXPENSES, "[]") ?: "[]"
        return runCatching {
            val json = JSONArray(source)
            List(json.length()) { index -> Expense.fromJson(json.getJSONObject(index)) }
        }.getOrDefault(emptyList())
    }

    fun find(id: String): Expense? = expenses().find { it.id == id }

    fun save(expense: Expense): Expense {
        val all = expenses().toMutableList()
        val index = all.indexOfFirst { it.id == expense.id }
        if (index >= 0) all[index] = expense else all.add(expense)
        persist(all)
        return expense
    }

    fun newId(): String = UUID.randomUUID().toString()

    fun delete(id: String) {
        persist(expenses().filterNot { it.id == id })
    }

    private fun persist(expenses: List<Expense>) {
        val json = JSONArray()
        expenses.forEach { json.put(it.asJson()) }
        preferences.edit().putString(KEY_EXPENSES, json.toString()).apply()
    }

    private companion object {
        const val PREFERENCES = "expense_demo"
        const val KEY_LOGGED_IN = "logged_in"
        const val KEY_EXPENSES = "expenses"
        const val DEMO_EMAIL = "qa.user@example.test"
        const val DEMO_PASSWORD = "Expense123!"
    }
}
