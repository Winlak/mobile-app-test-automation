package com.example.expenseautomationsut

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import java.math.RoundingMode

class ExpenseAdapter(private val onClick: (Expense) -> Unit) :
    RecyclerView.Adapter<ExpenseAdapter.ExpenseViewHolder>() {
    private var values: List<Expense> = emptyList()

    fun submit(items: List<Expense>) {
        values = items
        notifyDataSetChanged()
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ExpenseViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_expense, parent, false)
        return ExpenseViewHolder(view)
    }

    override fun onBindViewHolder(holder: ExpenseViewHolder, position: Int) {
        val expense = values[position]
        holder.bind(expense)
        holder.itemView.setOnClickListener { onClick(expense) }
    }

    override fun getItemCount(): Int = values.size

    class ExpenseViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        private val title = view.findViewById<TextView>(R.id.expense_item_title)
        private val details = view.findViewById<TextView>(R.id.expense_item_details)

        fun bind(expense: Expense) {
            title.text = expense.title
            details.text = "${expense.amount.setScale(2, RoundingMode.HALF_UP).toPlainString()} ₽ · ${expense.category}"
            itemView.contentDescription = "expense-row:${expense.id}"
        }
    }
}
