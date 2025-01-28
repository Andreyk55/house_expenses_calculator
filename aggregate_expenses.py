import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def format_int_no_decimals(value):
    """
    Formats a numeric value to comma-separated integer,
    unless it's between 0 and 1. If 0 < value < 1, return "<1".
    """
    if 0 < value < 1:
        return "<1"
    return f"{value:,.0f}"

def custom_pct(pct):
    """
    Custom function to format pie-chart percentages.
    If pct < 0.5, display '<1%' instead of '0%'.
    Otherwise, round to nearest integer (e.g. '12%').
    """
    return "<1%" if pct < 0.5 else f"{pct:.0f}%"

def plot_bar_and_pie(labels, values, title_label):
    """
    - Bar chart with numeric labels above each bar (comma-separated, no decimals).
    - Pie chart with slice sums, integer percentages (rounding),
      and a total-sum label in the center.
    - normalize=True ensures wedges reflect each value's fraction of sum(values).
    """

    # ----- Bar Chart -----
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, values, color='skyblue')
    ax.set_title(f"{title_label} - Bar Chart")
    ax.set_xlabel(title_label)
    ax.set_ylabel('Total Expense')
    ax.set_xticklabels(labels, rotation=45, ha='right')

    # Format the Y-axis as comma-separated, integer-only
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))

    # Add numeric labels above each bar
    for bar in bars:
        height = bar.get_height()
        x_position = bar.get_x() + bar.get_width() / 2
        label_text = format_int_no_decimals(height)
        ax.text(
            x_position,
            height,
            label_text,
            ha='center',
            va='bottom',
            fontsize=9
        )

    plt.tight_layout()
    plt.show()

    # ----- Pie Chart -----
    total_sum = values.sum()

    # IMPORTANT: normalize=True ensures each wedge is value/sum(values)
    fig, ax = plt.subplots(figsize=(8, 5))
    wedges, texts, autotexts = ax.pie(
        values,
        labels=None,
        autopct=custom_pct,
        startangle=140,
        normalize=True  # <-- Ensures correct sizing even if sum(values)<1 or any edge cases
    )
    ax.set_title(f"{title_label} - Pie Chart")

    # Display the total sum in the center of the pie
    ax.text(
        0, 0,
        f"Sum:\n{format_int_no_decimals(total_sum)}",
        ha='center',
        va='center',
        fontsize=12
    )

    # Customize each slice label: Name, slice sum, (pct)
    for i, autotext in enumerate(autotexts):
        slice_label = labels[i]
        slice_value = values[i]
        slice_pct = autotext.get_text()  # e.g., "12%", "<1%"
        slice_text = (
            f"{slice_label}\n"
            f"{format_int_no_decimals(slice_value)}\n"
            f"({slice_pct})"
        )
        autotext.set_text(slice_text)
        autotext.set_fontsize(9)

    plt.tight_layout()
    plt.show()

def main():
    """
    1) Read 'input_expenses.xlsx'; remove rows where total_expense is blank (NaN) or 0.
    2) Group by business_name, save to output.txt, plot bar + pie.
    3) Merge categories.xlsx if present, else 'Other'. Group by category, output + plot.
    """

    with open("output.txt", "w", encoding="utf-8") as f:
        # --- 1. Read Expenses ---
        df_expenses = pd.read_excel('input_expenses.xlsx')

        # Drop blank/NaN total_expense
        df_expenses.dropna(subset=['total_expense'], inplace=True)
        # Filter out zero
        df_expenses = df_expenses[df_expenses['total_expense'] != 0]
        # (Optional) Also ensure no negatives if your data shouldn't have them:
        # df_expenses = df_expenses[df_expenses['total_expense'] > 0]

        # --- Aggregate by BUSINESS NAME ---
        f.write("=== 1) Aggregation by Business Name ===\n")
        df_by_business = (
            df_expenses
            .groupby('buisness_name', as_index=False)['total_expense']
            .sum()
        )
        df_by_business.sort_values('total_expense', ascending=False, inplace=True)

        for _, row in df_by_business.iterrows():
            total_str = format_int_no_decimals(row['total_expense'])
            f.write(f"Business: {row['buisness_name']}, Total: {total_str}\n")

        plot_bar_and_pie(
            labels=df_by_business['buisness_name'],
            values=df_by_business['total_expense'],
            title_label="Business Name"
        )

        # --- Aggregate by CATEGORY ---
        f.write("\n=== 2) Aggregation by Category ===\n")

        if os.path.exists('categories.xlsx'):
            df_categories = pd.read_excel('categories.xlsx')
            df_merged = df_expenses.merge(df_categories, on='buisness_name', how='left')
            df_merged['category'] = df_merged['category'].fillna('Other')
        else:
            df_merged = df_expenses.copy()
            df_merged['category'] = 'Other'

        df_by_category = (
            df_merged
            .groupby('category', as_index=False)['total_expense']
            .sum()
        )
        df_by_category.sort_values('total_expense', ascending=False, inplace=True)

        for _, row in df_by_category.iterrows():
            total_str = format_int_no_decimals(row['total_expense'])
            f.write(f"Category: {row['category']}, Total: {total_str}\n")

        plot_bar_and_pie(
            labels=df_by_category['category'],
            values=df_by_category['total_expense'],
            title_label="Category"
        )

if __name__ == "__main__":
    main()
