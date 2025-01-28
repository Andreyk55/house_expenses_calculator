import os
import pandas as pd
import matplotlib.pyplot as plt

def plot_bar_and_pie(labels, values, title_label):
    """
    Helper function to plot a bar chart and a pie chart for given labels/values.
    Displays:
      - Bar chart with axis labels.
      - Pie chart with each slice showing:
          * The label (category / business name).
          * The absolute sum for that slice.
          * The percentage of the total.
        And in the center, shows the total sum.
    """

    # ----- Bar Chart -----
    plt.figure(figsize=(8, 5))
    plt.bar(labels, values, color='skyblue')
    plt.title(f"{title_label} - Bar Chart")
    plt.xlabel(title_label)
    plt.ylabel('Total Expense')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

    # ----- Pie Chart -----
    total_sum = values.sum()  # Calculate total for this set

    # We first draw a pie chart without the standard labels, so we can override them
    fig, ax = plt.subplots(figsize=(8, 5))
    wedges, texts, autotexts = ax.pie(
        values,
        labels=None,         # We'll create custom labels below
        autopct='%1.1f%%',   # This will give us the slice's percentage
        startangle=140
    )
    ax.set_title(f"{title_label} - Pie Chart")

    # Center text: show total sum
    # (0,0) is the center of the pie chart in data coordinates
    ax.text(
        0, 0,
        f"Sum:\n{total_sum:.2f}",
        ha='center',
        va='center',
        fontsize=12
    )

    # Customize each slice’s label to show: Category/Business, slice sum, and percentage
    for i, autotext in enumerate(autotexts):
        slice_label = labels[i]
        slice_value = values[i]
        slice_pct = autotext.get_text()  # e.g. "12.3%"
        # Build a multiline label
        # Example: "Food\n123.45\n(12.3%)"
        new_label = f"{slice_label}\n{slice_value:.2f}\n({slice_pct})"
        autotext.set_text(new_label)
        autotext.set_fontsize(9)  # Adjust if you want bigger/smaller text

    plt.tight_layout()
    plt.show()

def main():
    """
    1. Aggregate by 'buisness_name' -> print + bar/pie charts (with slice sums).
    2. Aggregate by 'category' ->
       - Attempt to read 'categories.xlsx'.
       - If file not found or if some buisness_name not matched => category = 'Other'.
       - Print + bar/pie charts (with slice sums).
    """

    # ----- 1. Read Expenses -----
    df_expenses = pd.read_excel('input_expenses.xlsx')  
    # Expecting columns: 'buisness_name' (string), 'total_expense' (float)

    # =============================
    #  AGGREGATE BY BUSINESS NAME
    # =============================
    print("=== 1) Aggregation by Business Name ===")
    df_by_business = (
        df_expenses
        .groupby('buisness_name', as_index=False)['total_expense']
        .sum()
    )
    # Sort descending
    df_by_business.sort_values('total_expense', ascending=False, inplace=True)

    # Print results in console
    for _, row in df_by_business.iterrows():
        print(f"Business: {row['buisness_name']}, Total: {row['total_expense']}")

    # Plot bar + pie
    plot_bar_and_pie(
        labels=df_by_business['buisness_name'],
        values=df_by_business['total_expense'],
        title_label="Business Name"
    )

    # =============================
    #  AGGREGATE BY CATEGORY
    # =============================
    print("\n=== 2) Aggregation by Category ===")

    # Check if categories.xlsx exists
    if os.path.exists('categories.xlsx'):
        # Read categories
        df_categories = pd.read_excel('categories.xlsx')  
        # Expecting columns: 'buisness_name', 'category'

        # Left merge -> keep all expenses, bring in category if matched
        df_merged = df_expenses.merge(df_categories, on='buisness_name', how='left')

        # Any missing categories => 'Other'
        df_merged['category'] = df_merged['category'].fillna('Other')
    else:
        # No categories file -> everything goes to 'Other'
        df_merged = df_expenses.copy()
        df_merged['category'] = 'Other'

    df_by_category = (
        df_merged
        .groupby('category', as_index=False)['total_expense']
        .sum()
    )
    df_by_category.sort_values('total_expense', ascending=False, inplace=True)

    # Print results in console
    for _, row in df_by_category.iterrows():
        print(f"Category: {row['category']}, Total: {row['total_expense']}")

    # Plot bar + pie
    plot_bar_and_pie(
        labels=df_by_category['category'],
        values=df_by_category['total_expense'],
        title_label="Category"
    )

if __name__ == "__main__":
    main()
