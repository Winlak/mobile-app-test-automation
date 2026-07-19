package com.example.expenseautomationsut

import org.json.JSONObject
import java.math.BigDecimal

data class Expense(
    val id: String,
    val title: String,
    val amount: BigDecimal,
    val category: String,
) {
    fun asJson(): JSONObject = JSONObject()
        .put("id", id)
        .put("title", title)
        .put("amount", amount.toPlainString())
        .put("category", category)

    companion object {
        fun fromJson(json: JSONObject): Expense = Expense(
            id = json.getString("id"),
            title = json.getString("title"),
            amount = json.getString("amount").toBigDecimal(),
            category = json.getString("category"),
        )
    }
}
