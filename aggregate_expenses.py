import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def format_int_no_decimals(value):
    """
    Converts a numeric value to comma-separated integer, unless it's 0 < value < 1.
    In that case, returns '<1'.
    Example:
      1234.56 -> '1,235'
      0.3     -> '<1'
    """
    if 0 < value < 1:
        return "<1"
    return f"{value:,.0f}"

def custom_bar_percentage(value, total_sum):
    """
    Computes the percentage of 'value' relative to 'total_sum'.
      - If total_sum == 0, returns '0%'
      - If < 0.5%, returns '<1%'
      - Otherwise, round to nearest integer, e.g. '12%'.
    """
    if total_sum == 0:
        return "0%"
    pct = (value / total_sum) * 100
    return "<1%" if (0 < pct < 0.5) else f"{pct:.0f}%"

def custom_slice_label(slice_label, slice_value, slice_pct):
    """
    Builds a multi-line string for each pie slice:
      1) The label (category/business name)
      2) The absolute value (comma-separated, no decimals, or <1)
      3) The percentage, e.g., '12%' or '<1%'
    """
    value_str = format_int_no_decimals(slice_value)
    return f"{slice_label}\n{value_str}\n({slice_pct})"

def plot_bar_chart(labels, values, title_label):
    """
    Creates a bar chart where each bar's label shows:
      - Absolute value (no decimals, commas, <1 if small)
      - Percentage of the total in parentheses, e.g., '(12%)' or '(<1%)'.
    Also places a 'Total: X' label at the top-right corner of the chart.
    """
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, values, color='skyblue')

    ax.set_title(f"{title_label} - Bar Chart")
    ax.set_xlabel(title_label)
    ax.set_ylabel('Total Expense')
    ax.set_xticklabels(labels, rotation=45, ha='right')

    # Format Y-axis as comma-separated integers
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))

    total_sum = values.sum()

    # Label each bar: absolute value + percentage
    for bar in bars:
        height = bar.get_height()
        x_position = bar.get_x() + bar.get_width() / 2
        val_str = format_int_no_decimals(height)
        pct_str = custom_bar_percentage(height, total_sum)
        label_text = f"{val_str}\n({pct_str})"

        ax.text(
            x_position,
            height,
            label_text,
            ha='center',
            va='bottom',
            fontsize=9
        )

    # ---- NEW: Show "Total: X" in the top-right corner ----
    total_str = format_int_no_decimals(total_sum)
    ax.text(
        0.95, 0.95,                # x,y in axes coords (0=left/bottom, 1=right/top)
        f"Total: {total_str}",
        transform=ax.transAxes,    # specify that 0.95,0.95 is relative to axes
        ha='right',
        va='top',
        fontsize=11,
        fontweight='bold'
    )

    plt.tight_layout()
    plt.show()

def plot_fraction_pie(labels, values, title_label):
    """
    Creates a pie chart by passing FRACTIONS (values / sum(values)), ensuring correct wedge sizes.
    Slice label includes:
      1) Category/Business Name
      2) Absolute Value
      3) Percentage (rounded or <1%)
    Displays total sum in the center.
    """
    total_sum = values.sum()
    if total_sum == 0:
        print(f"[INFO] No non-zero data for {title_label}, skipping pie chart.")
        return

    fractions = values / total_sum  # fraction of total

    fig, ax = plt.subplots(figsize=(8, 5))

    # autopct='%0.0f%%' => integer % or "0%" => we'll replace "0%" with "<1%" below
    wedges, texts, autotexts = ax.pie(
        fractions,
        labels=None,
        autopct='%0.0f%%',
        startangle=140
    )

    ax.set_title(f"{title_label} - Pie Chart")

    # Center text => total sum
    sum_str = format_int_no_decimals(total_sum)
    ax.text(
        0, 0,
        f"Sum:\n{sum_str}",
        ha='center',
        va='center',
        fontsize=12
    )

    # Override each slice label
    for i, autotext in enumerate(autotexts):
        slice_label = labels[i]
        slice_value = values[i]
        pct_text = autotext.get_text().strip()
        if pct_text == "0%":
            pct_text = "<1%"

        new_label = custom_slice_label(slice_label, slice_value, pct_text)
        autotext.set_text(new_label)
        autotext.set_fontsize(9)

    plt.tight_layout()
    plt.show()

def main():
    """
    1. Read 'input_expenses.xlsx', remove blank/NaN or zero total_expense.
    2. Aggregate by 'buisness_name', write to output.txt, bar + pie charts.
    3. Merge categories if available -> aggregate by 'category', write + bar/pie.
    """
    with open("output.txt", "w", encoding="utf-8") as f:

        # --- 1) Read & Filter Expenses ---
        df_expenses = pd.read_excel('input_expenses.xlsx')
        df_expenses.dropna(subset=['total_expense'], inplace=True)
        df_expenses = df_expenses[df_expenses['total_expense'] != 0]
        # Optionally remove negatives if not allowed:
        # df_expenses = df_expenses[df_expenses['total_expense'] > 0]

        # --- 2) Aggregate by BUSINESS NAME ---
        f.write("=== 1) Aggregation by Business Name ===\n")

        df_by_business = (
            df_expenses
            .groupby('buisness_name', as_index=False)['total_expense']
            .sum()
        )
        df_by_business.sort_values('total_expense', ascending=False, inplace=True)

        for _, row in df_by_business.iterrows():
            val_str = format_int_no_decimals(row['total_expense'])
            f.write(f"Business: {row['buisness_name']}, Total: {val_str}\n")

        # Plot bar + fraction-pie
        plot_bar_chart(
            labels=df_by_business['buisness_name'],
            values=df_by_business['total_expense'],
            title_label="Business Name"
        )
        plot_fraction_pie(
            labels=df_by_business['buisness_name'],
            values=df_by_business['total_expense'],
            title_label="Business Name"
        )

        # --- 3) Aggregate by CATEGORY ---
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
            val_str = format_int_no_decimals(row['total_expense'])
            f.write(f"Category: {row['category']}, Total: {val_str}\n")

        # Plot bar + fraction-pie
        plot_bar_chart(
            labels=df_by_category['category'],
            values=df_by_category['total_expense'],
            title_label="Category"
        )
        plot_fraction_pie(
            labels=df_by_category['category'],
            values=df_by_category['total_expense'],
            title_label="Category"
        )

if __name__ == "__main__":
    main()
