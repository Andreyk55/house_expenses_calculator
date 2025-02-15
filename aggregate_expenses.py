import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import mplcursors  # <-- for interactive annotations
import numpy as np

def is_all_hebrew(word: str) -> bool:
    """
    Returns True if 'word' consists ONLY of Hebrew letters (\u0590-\u05FF).
    Otherwise False (digits, punctuation, or mixing => not purely Hebrew).
    """
    return bool(re.match(r'^[\u0590-\u05FF]+$', word)) or word.__contains__('"') or word.__contains__('-') or word.__contains__('/')

def reverse_line_hebrew_words_and_order(line: str) -> str:
    """
    1) Split 'line' by spaces into tokens.
    2) Reverse the entire token list order.
    3) For each token that is fully Hebrew, also reverse its letters.
    4) Join back with spaces.
    
    Example:
      "שלום עולם" => ["שלום", "עולם"] => reverse => ["עולם", "שלום"] 
                     => reverse letters => ["םלוע", "םולש"] => "םלוע םולש"
      "שלום123" => single token with digits => unchanged => "שלום123"
    """
    tokens = line.split()
    # Reverse the overall word order
    tokens.reverse()

    new_tokens = []
    for token in tokens:
        if is_all_hebrew(token):
            # Reverse the letters
            token = token[::-1]
        new_tokens.append(token)
    # Join final list
    return " ".join(new_tokens)

def format_int_no_decimals(value):
    """
    Converts a numeric value to a comma-separated integer, unless it's 0 < value < 1.
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
    Normal bar chart for e.g. 'Business Name' (without interactive details).
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

    # Show "Total: X" in the top-right corner
    total_str = format_int_no_decimals(total_sum)
    ax.text(
        0.95, 0.95,
        f"Total: {total_str}",
        transform=ax.transAxes,
        ha='right',
        va='top',
        fontsize=11,
        fontweight='bold'
    )

    plt.tight_layout()
    plt.show()

def plot_bar_chart_with_details(labels, values, title_label, category_details):
    labels = labels.reset_index(drop=True)

    """
    Bar chart specifically for 'Category' with an interactive annotation on click.
    category_details: dict mapping category_name -> list of (business, expense_str)
    Using NAIVE reversal for Hebrew text in the annotation popup.
    """
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, values, color='skyblue')

    ax.set_title(f"{title_label} - Bar Chart (Interactive)")
    ax.set_xlabel(title_label)
    ax.set_ylabel('Total Expense')
    ax.set_xticklabels(labels, rotation=45, ha='right')

    # Format Y-axis as comma-separated integers
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))

    total_sum = values.sum()

    # Label each bar with absolute + percentage
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

    # "Total: X" top-right
    total_str = format_int_no_decimals(total_sum)
    ax.text(
        0.95, 0.95,
        f"Total: {total_str}",
        transform=ax.transAxes,
        ha='right',
        va='top',
        fontsize=11,
        fontweight='bold'
    )

    # --------------------------
    #  Use mplcursors for click
    # --------------------------
    cursor = mplcursors.cursor(bars, hover=False)  # or hover=True if you want mouseover

    @cursor.connect("add")
    def on_add(sel):
        print('------------------')
        print(sel)
        idx = sel.index
        cat_label = labels[idx]
        biz_info_list = category_details.get(cat_label, [])

        # Build lines
        lines = [f"Category: {cat_label}"]
        for (biz_name, exp_str) in biz_info_list:
            # Also apply naive reversal to the business name
            biz_name_reversed = reverse_line_hebrew_words_and_order(biz_name)
            lines.append(f"{biz_name_reversed} => {exp_str}")

        # Join with newlines
        detail_text = "\n".join(lines)

        # Set the annotation text to show these details
        sel.annotation.set_text(detail_text)

        # Optional styling
        sel.annotation.get_bbox_patch().set(fc="white", ec="black")

    plt.tight_layout()
    plt.show()

def plot_fraction_pie(labels, values, title_label):
    """
    Pie chart with fraction-based wedge sizing.
    """
    total_sum = values.sum()
    if total_sum == 0:
        print(f"[INFO] No non-zero data for {title_label}, skipping pie chart.")
        return

    fractions = values / total_sum

    fig, ax = plt.subplots(figsize=(8, 5))

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
    plot_by_business = False

    """
    1. Read 'input_expenses.xlsx', remove blank/NaN or zero total_expense.
    2. Optionally aggregate by 'buisness_name', bar + pie charts.
    3. Merge categories if available -> aggregate by 'category'.
       - Build a dictionary of each category's business breakdown.
       - Show interactive bar chart (naive reversing Hebrew text on click).
    """
    with open("output.txt", "w", encoding="utf-8") as f:

        # --- 1) Read & Filter Expenses ---
        df_expenses = pd.read_excel('input_expenses.xlsx')
        df_expenses.dropna(subset=['total_expense'], inplace=True)
        df_expenses = df_expenses[df_expenses['total_expense'] != 0]
        # (Optional) remove negatives if not allowed:
        # df_expenses = df_expenses[df_expenses['total_expense'] > 0]

        if plot_by_business:
            # --- 2) Aggregate by BUSINESS NAME ---
            f.write("=== 1) Aggregation by Business Name ===\n")
            df_by_business = (
                df_expenses
                .groupby('buisness_name', as_index=False)['total_expense']
                .sum()
            )
            df_by_business.sort_values('total_expense', ascending=False, inplace=True)

            for _, row_biz in df_by_business.iterrows():
                val_str = format_int_no_decimals(row_biz['total_expense'])
                f.write(f"Business: {row_biz['buisness_name']}, Total: {val_str}\n")

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

        # Merge with categories if available
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
        
        df_by_category_not_sorted = df_by_category.copy()
        df_by_category.sort_values('total_expense', ascending=False, inplace=True)

        category_details = {}
        for _, row_cat in df_by_category.iterrows():
            cat = row_cat['category']
            cat_total = row_cat['total_expense']
            cat_total_str = format_int_no_decimals(cat_total)
            f.write(f"Category: {cat}, Total: {cat_total_str}\n")

            # For each category, gather business breakdown
            cat_df = (
                df_merged[df_merged['category'] == cat]
                .groupby('buisness_name', as_index=False)['total_expense']
                .sum()
                .sort_values('total_expense', ascending=False)
            )

            detail_list = []
            for _, row_b in cat_df.iterrows():
                biz_name = row_b['buisness_name']
                biz_exp_str = format_int_no_decimals(row_b['total_expense'])
                detail_list.append((biz_name, biz_exp_str))
                f.write(f"\tBusiness: {biz_name} => {biz_exp_str}\n")

            category_details[cat] = detail_list

        # Now we have 'df_by_category' for the bar/pie, and 'category_details' for the popup
        # Plot an interactive bar chart for Category
        plot_bar_chart_with_details(
            labels=df_by_category['category'],
            values=df_by_category['total_expense'],
            title_label="Category",
            category_details=category_details
        )
        # And a standard pie chart for Category
        plot_fraction_pie(
            labels=df_by_category['category'],
            values=df_by_category['total_expense'],
            title_label="Category"
        )

if __name__ == "__main__":
    main()
