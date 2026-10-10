import pandas as pd

df = pd.read_csv("../Data/ecommerce_sales_raw.csv")

# print(df.head())
# print(df.shape)
# print(df.columns)
# print(df.info())
# print(df.describe())


# Standardize text columns by removing extra spaces and using consistent capitalization
text_columns = [
    "Gender",
    "City",
    "State",
    "Product",
    "Category",
    "Sub_Category",
    "Payment_Mode",
    "Order_Status"
]

for col in text_columns:
    df[col] = df[col].str.strip().str.title()


# Count the number of missing values in every column
print(df.isnull().sum())
print(df["Order_Status"].value_counts())
df = df.drop_duplicates()
print("Duplicate rows-", df.duplicated().sum())


# Count missing delivery dates separately for each order status
print(
    df.groupby("Order_Status")["Delivery_Date"]
      .apply(lambda x: x.isnull().sum())
)
print(
    df.groupby("Order_Status")["Rating"]
      .apply(lambda x: x.isnull().sum())
)

missing_delivery = df[
    (df["Order_Status"] == "Delivered") &
    (df["Delivery_Date"].isnull())
]

print(missing_delivery[
    [
        "Order_ID",
        "Customer_ID",
        "Product",
        "Order_Date",
        "Delivery_Date",
        "Order_Status"
    ]
])

# Select only Returned orders where Delivery_Date is available
returned_orders = df[
    (df["Order_Status"] == "Returned") &
    (df["Delivery_Date"].notnull())
]

print(
    returned_orders["Delivery_Date"].isnull().value_counts()
)

print(
    returned_orders[
        ["Order_ID", "Product", "Order_Date", "Delivery_Date", "Rating"]
    ]
)

# Find all rows where the City value is missing
missing_city = df[df["City"].isnull()]
print(missing_city[["Customer_ID", "Customer_Name", "State", "City"]])
# Check all orders of customer CUST1050 to see whether their City is available in another order
print(
    df[df["Customer_ID"] == "CUST1050"][
        ["Customer_ID", "Customer_Name", "State", "City"]
    ]
)

# Find the first available City for each customer and return it for every row of that customer
customer_city = df.groupby("Customer_ID")["City"].transform("first")


# Compare missing City values with the City recovered from the customer's other orders
print(
    df.loc[df["City"].isnull(),
           ["Customer_ID", "Customer_Name", "State", "City"]]
    .assign(Recovered_City=customer_city)
)
# Check whether any customer has more than one unique City in their existing orders
city_consistency = df.groupby("Customer_ID")["City"].nunique()
print(city_consistency[city_consistency > 1])

# Fill the missing City values using the recovered City of the same customer
df["City"] = df["City"].fillna(customer_city)

# Verify that no missing City values remain
print(df["City"].isnull().sum())
# Display the data type of every column in our dataset
print(df.dtypes)


# Convert Order_Date from string/text format into Pandas datetime format
df["Order_Date"] = pd.to_datetime(df["Order_Date"])
# Convert Delivery_Date from string/text format into Pandas datetime format while keeping missing dates as NaT
df["Delivery_Date"] = pd.to_datetime(df["Delivery_Date"])
# Verify the data types of all columns after date conversion
print(df.dtypes)

# Find orders where the Delivery_Date is earlier than the Order_Date
invalid_dates = df[
    df["Delivery_Date"] < df["Order_Date"]
]

# Display the orders with invalid date relationships
print(
    invalid_dates[
        ["Order_ID", "Order_Date", "Delivery_Date", "Order_Status"]
    ]
)


# 4️⃣Sales Metrics calculation
# STEP 4.1 — Calculate total sales amount before applying any discount
df["Gross_Sales"] = df["Quantity"] * df["Unit_Price"]


# STEP 4.2 — Calculate the actual discount amount in currency
df["Discount_Amount"] = (
    df["Gross_Sales"] * df["Discount"] / 100
)


# STEP 4.3 — Calculate the final sales amount after applying the discount
df["Net_Sales"] = (
    df["Gross_Sales"] - df["Discount_Amount"]
)


# STEP 4.4 — Display the newly created sales metrics for the first five orders
print(
    df[
        [
            "Order_ID",
            "Quantity",
            "Unit_Price",
            "Discount",
            "Gross_Sales",
            "Discount_Amount",
            "Net_Sales"
        ]
    ].head()
)

#5️⃣Overall sales performance
#5.1 Calculate the overall sales performance of the e-commerce business
total_gross_sales = df["Gross_Sales"].sum()
total_discount = df["Discount_Amount"].sum()
total_net_sales = df["Net_Sales"].sum()

#5.2 Calculate the average net sales per order
average_order_value = df["Net_Sales"].mean()

#5.3 Count the total number of orders
total_orders = df["Order_ID"].nunique()

#5.4 Display the overall sales KPIs
print("Total Orders:", total_orders)
print("Total Gross Sales:", total_gross_sales)
print("Total Discount:", total_discount)
print("Total Net Sales:", total_net_sales)
print("Average Order Value:", average_order_value)


#6️⃣Order status analysis
#6.1 Calculate total orders and sales metrics for each Order_Status
status_analysis = df.groupby("Order_Status").agg(
    Total_Orders=("Order_ID", "nunique"),
    Gross_Sales=("Gross_Sales", "sum"),
    Discount_Amount=("Discount_Amount", "sum"),
    Net_Sales=("Net_Sales", "sum")
)

# Display the sales performance by order status
print("Status Analysis:", status_analysis)

#6.2 Calculate the percentage of orders in each order status
status_percentage = (
    df["Order_Status"]
    .value_counts(normalize=True)
    * 100
)
# Display the percentage distribution of order statuses
print(status_percentage)

#7️⃣Category wise sales analysis
#7.1 Calculate sales performance for each product category
category_sales = df.groupby("Category").agg(
    Total_Orders=("Order_ID", "nunique"),
    Gross_Sales=("Gross_Sales", "sum"),
    Discount_Amount=("Discount_Amount", "sum"),
    Net_Sales=("Net_Sales", "sum")
).sort_values(
    "Net_Sales",
    ascending=False
)

# Display categories from highest to lowest Net Sales
print(category_sales)

#7.2 Calculate the average order value for each product category
category_aov = df.groupby("Category").agg(
    Total_Orders=("Order_ID", "nunique"),
    Total_Net_Sales=("Net_Sales", "sum")
)

# Calculate average revenue generated per order in each category
category_aov["Average_Order_Value"] = (
    category_aov["Total_Net_Sales"] /
    category_aov["Total_Orders"]
)

# Sort categories from highest to lowest average order value
category_aov = category_aov.sort_values(
    "Average_Order_Value",
    ascending=False
)

# Display the category-wise average order value
print(category_aov)

#8️⃣Product wise sales analysis
#8.1 Calculate sales performance for each individual product
product_sales = df.groupby("Product").agg(
    Total_Orders=("Order_ID", "nunique"),
    Gross_Sales=("Gross_Sales", "sum"),
    Discount_Amount=("Discount_Amount", "sum"),
    Net_Sales=("Net_Sales", "sum")
).sort_values(
    "Net_Sales",
    ascending=False
)

# Display the top 10 products based on Net Sales
print(product_sales.head(10))

#8.2 Calculate total Net Sales across the entire dataset
total_net_sales = df["Net_Sales"].sum()
# Calculate Net Sales for each product
product_contribution = df.groupby("Product").agg(
    Total_Orders=("Order_ID", "nunique"),
    Net_Sales=("Net_Sales", "sum")
)
# Calculate each product's percentage contribution to total Net Sales
product_contribution["Sales_Contribution_%"] = (
    product_contribution["Net_Sales"] / total_net_sales * 100
)
# Sort products from highest to lowest sales contribution
product_contribution = product_contribution.sort_values(
    "Sales_Contribution_%",
    ascending=False
)
# Display the top 10 products and their contribution to total sales
print(product_contribution.head(10))

#9️⃣Customer analysis
#9.1 Count the total number of unique customers in the dataset
total_customers = df["Customer_ID"].nunique()
# Display the total number of unique customers
print("Total Unique Customers:", total_customers)

#9.2 Count how many orders each customer has placed
customer_orders = df.groupby("Customer_ID")["Order_ID"].nunique()
# Display the number of orders placed by each customer
print(customer_orders.head())

#9.3 Classify each customer based on how many orders they have placed
customer_type = customer_orders.apply(
    lambda x: "One-time Customer" if x == 1 else "Repeat Customer"
)

#9.4 Count how many customers belong to each customer type
customer_type_count = customer_type.value_counts()
# Display the number of one-time and repeat customers
print(customer_type_count)
# Calculate the percentage distribution of one-time and repeat customers
customer_type_percentage = (
    customer_type.value_counts(normalize=True) * 100
)
# Display the customer type percentages
print(customer_type_percentage)

#9.5 Calculate total orders and total Net Sales generated by each customer
customer_value = df.groupby("Customer_ID").agg(
    Total_Orders=("Order_ID", "nunique"),
    Total_Net_Sales=("Net_Sales", "sum")
)
# Sort customers from highest to lowest based on Net Sales
customer_value = customer_value.sort_values(
    "Total_Net_Sales",
    ascending=False
)
# Display the top 10 customers by Net Sales
print(customer_value.head(10))

#9.6 Calculate the average amount spent by each customer per order
customer_value["Customer_AOV"] = (
    customer_value["Total_Net_Sales"] /
    customer_value["Total_Orders"]
)
# Sort customers by their average order value
customer_aov = customer_value.sort_values(
    "Customer_AOV",
    ascending=False
)
# Display the top 10 customers by average order value
print(customer_aov.head(10))

#9.7 Find the sales thresholds that divide customers into quartile groups
q1 = customer_value["Total_Net_Sales"].quantile(0.25)
q3 = customer_value["Total_Net_Sales"].quantile(0.75)
print("25th Percentile:", q1)
print("75th Percentile:", q3)

#9.8 Create customer segments based on their total Net Sales
customer_value["Customer_Segment"] = customer_value["Total_Net_Sales"].apply(
    lambda x:
        "Low Value" if x <= q1
        else "High Value" if x >= q3
        else "Medium Value"
)
# Count how many customers are present in each segment
segment_count = customer_value["Customer_Segment"].value_counts()
# Display the number of customers in each segment
print(segment_count)

#9.9 Group customers by their segment and calculate customer count and total revenue
segment_analysis = customer_value.groupby("Customer_Segment").agg(
    Customers=("Total_Net_Sales", "count"),
    Total_Net_Sales=("Total_Net_Sales", "sum")
)

#9.9 Calculate each segment's contribution to total revenue
segment_analysis["Revenue_Contribution_%"] = (
    segment_analysis["Total_Net_Sales"]
    / segment_analysis["Total_Net_Sales"].sum()
    * 100
)
# Display the segment analysis
print(segment_analysis)

#1️⃣0️⃣Product analysis
#10.1 Create a Month-Year column from Order_Date for monthly sales analysis
df["Month_year"] = df["Order_Date"].dt.to_period("M")
# Display the first few Month-Year values
print(df[["Order_Date","Month_year"]].head())

# Group the orders by Month-Year and calculate monthly business performance
monthly_sales = df.groupby("Month_year").agg(
    Total_Orders=("Order_ID", "nunique"),
    Gross_Sales=("Gross_Sales", "sum"),
    Discount_Amount=("Discount_Amount", "sum"),
    Net_Sales=("Net_Sales", "sum")
)
# Display the monthly sales summary
print(monthly_sales)

# Calculate the average Net Sales generated per order in each month
monthly_sales["Monthly_AOV"] = (
    monthly_sales["Net_Sales"] /
    monthly_sales["Total_Orders"]
)
# Display monthly orders, Net Sales and AOV
print(
    monthly_sales[
        ["Total_Orders", "Net_Sales", "Monthly_AOV"]
    ]
)

# Identify the month with the highest and lowest Net Sales
best_month = monthly_sales["Net_Sales"].idxmax()
worst_month = monthly_sales["Net_Sales"].idxmin()
print("Best Month:", best_month)
print("Highest Net Sales:", monthly_sales.loc[best_month, "Net_Sales"])
print("Worst Month:", worst_month)
print("Lowest Net Sales:", monthly_sales.loc[worst_month, "Net_Sales"])

# Calculate the month-over-month percentage change in Net Sales
monthly_sales["MoM_Growth_%"] = (
    monthly_sales["Net_Sales"].pct_change() * 100
)
# Display monthly Net Sales and growth rate
print(
    monthly_sales[
        ["Net_Sales", "MoM_Growth_%"]
    ]
)


# Find the month with the highest positive MoM growth
highest_growth_month = monthly_sales["MoM_Growth_%"].idxmax()
# Find the month with the largest negative MoM growth
highest_decline_month = monthly_sales["MoM_Growth_%"].idxmin()
# Display the months and their growth rates
print("Highest Growth Month:", highest_growth_month)
print(
    "Highest Growth Rate:",
    monthly_sales.loc[highest_growth_month, "MoM_Growth_%"]
)
print("Highest Decline Month:", highest_decline_month)
print(
    "Highest Decline Rate:",
    monthly_sales.loc[highest_decline_month, "MoM_Growth_%"]
)

# Analyze order volume and revenue performance for each order status
status_analysis = df.groupby("Order_Status").agg(
    Total_Orders=("Order_ID", "nunique"),
    Gross_Sales=("Gross_Sales", "sum"),
    Discount_Amount=("Discount_Amount", "sum"),
    Net_Sales=("Net_Sales", "sum")
)
# Calculate the percentage of total orders represented by each status
status_analysis["Order_Contribution_%"] = (
    status_analysis["Total_Orders"]
    / status_analysis["Total_Orders"].sum()
    * 100
)
# Display the order status analysis
print(status_analysis)


# Calculate the percentage of total orders that were cancelled or returned
cancellation_rate = (
    status_analysis.loc["Cancelled", "Total_Orders"]
    / status_analysis["Total_Orders"].sum()
    * 100
)
return_rate = (
    status_analysis.loc["Returned", "Total_Orders"]
    / status_analysis["Total_Orders"].sum()
    * 100
)
# Display the cancellation and return rates
print("Cancellation Rate:", cancellation_rate)
print("Return Rate:", return_rate)


# Calculate the total Net Sales value associated with cancelled and returned orders
problematic_sales = (
    status_analysis.loc["Cancelled", "Net_Sales"]
    + status_analysis.loc["Returned", "Net_Sales"]
)
# Calculate what percentage of total Net Sales is associated with problematic orders
problematic_sales_percentage = (
    problematic_sales
    / status_analysis["Net_Sales"].sum()
    * 100
)
# Display the revenue exposure
print("Cancelled + Returned Net Sales:", problematic_sales)
print("Revenue Exposure %:", problematic_sales_percentage)

# Calculate the average Net Sales per order for each order status
status_analysis["Status_AOV"] = (
    status_analysis["Net_Sales"]
    / status_analysis["Total_Orders"]
)
# Display order count, Net Sales and AOV by order status
print(
    status_analysis[
        ["Total_Orders", "Net_Sales", "Status_AOV"]
    ]
)


# Calculate the Net Sales generated from successfully delivered orders
delivered_sales = status_analysis.loc["Delivered", "Net_Sales"]
# Calculate what percentage of total Net Sales comes from delivered orders
delivered_sales_percentage = (
    delivered_sales
    / status_analysis["Net_Sales"].sum()
    * 100
)
# Display the Delivered Sales and its contribution to total Net Sales
print("Delivered Sales:", delivered_sales)
print("Delivered Sales Contribution %:", delivered_sales_percentage)

# Count cancelled, delivered and returned orders for each product category
category_status = pd.crosstab(
    df["Category"],
    df["Order_Status"]
)
# Display the category-wise order status distribution
print(category_status)

# Calculate the total number of orders in each category
category_total_orders = category_status.sum(axis=1)

# Calculate cancellation rate for each category
category_status["Cancellation_Rate_%"] = (
    category_status["Cancelled"]
    / category_total_orders
    * 100
)

# Calculate return rate for each category
category_status["Return_Rate_%"] = (
    category_status["Returned"]
    / category_total_orders
    * 100
)
# Display category-wise cancellation and return rates
print(
    category_status[
        ["Cancelled", "Delivered", "Returned",
         "Cancellation_Rate_%", "Return_Rate_%"]
    ]
)


# Calculate the overall problematic order rate for each category
# Problematic orders = Cancelled orders + Returned orders
category_status["Problematic_Order_Rate_%"] = (
    (category_status["Cancelled"] + category_status["Returned"])
    / category_total_orders
    * 100
)
# Display the category-wise problematic order rate
print(
    category_status[
        ["Cancelled", "Returned", "Problematic_Order_Rate_%"]
    ]
)


#Step 11 customer category Behaviour
#11.1 Count how many orders each customer has placed
customer_order_count = df.groupby("Customer_ID")["Order_ID"].nunique()
# Display the number of orders placed by each customer
print(customer_order_count.head())

# Classify customers based on how many orders they have placed
customer_type = customer_order_count.apply(
    lambda x: "One-time Customer" if x == 1 else "Repeat Customer"
)
# Count how many customers belong to each customer type
customer_type_count = customer_type.value_counts()
# Display the customer type distribution
print(customer_type_count)

# Calculate the percentage of customers in each customer type
customer_type_percentage = (
    customer_type_count
    / customer_type_count.sum()
    * 100
)
# Display the percentage distribution of customer types
print(customer_type_percentage)


# Add the customer type classification to every order in the main dataset
df["Customer_Type"] = df["Customer_ID"].map(customer_type)
# Calculate total Net Sales generated by each customer type
customer_type_sales = df.groupby("Customer_Type")["Net_Sales"].sum()
# Calculate each customer type's percentage contribution to total Net Sales
customer_type_sales_percentage = (
    customer_type_sales
    / customer_type_sales.sum()
    * 100
)
# Combine sales and percentage contribution into one table
customer_sales_analysis = pd.DataFrame({
    "Total_Net_Sales": customer_type_sales,
    "Sales_Contribution_%": customer_type_sales_percentage
})
# Display the result
print(customer_sales_analysis)

# Count how many customers made 1, 2, 3, ... orders
purchase_frequency = customer_order_count.value_counts().sort_index()
# Display the purchase frequency distribution
print(purchase_frequency)

# Calculate the average number of orders placed per customer
average_orders_per_customer = customer_order_count.mean()
print("Average Orders per Customer:", average_orders_per_customer)

# Calculate total orders and total Net Sales for each customer
customer_value = df.groupby("Customer_ID").agg(
    Total_Orders=("Order_ID", "nunique"),
    Total_Net_Sales=("Net_Sales", "sum")
)

# Calculate the average order value for each customer
customer_value["Customer_AOV"] = (
    customer_value["Total_Net_Sales"]
    / customer_value["Total_Orders"]
)
# Display the top 10 customers based on total Net Sales
print(
    customer_value
    .sort_values("Total_Net_Sales", ascending=False)
    .head(10)
)

# Calculate the 25th percentile of customer total Net Sales
low_threshold = customer_value["Total_Net_Sales"].quantile(0.25)
# Calculate the 75th percentile of customer total Net Sales
high_threshold = customer_value["Total_Net_Sales"].quantile(0.75)
print("25th Percentile:", low_threshold)
print("75th Percentile:", high_threshold)


# Segment customers based on their total Net Sales ⭐⭐⭐
customer_value["Customer_Segment"] = pd.cut(
    customer_value["Total_Net_Sales"],
    bins=[
        -float("inf"),
        low_threshold,
        high_threshold,
        float("inf")
    ],
    labels=[
        "Low Value",
        "Medium Value",
        "High Value"
    ]
)
# Count customers in each segment
segment_count = customer_value["Customer_Segment"].value_counts()
print(segment_count)

# Analyze revenue generated by each customer segment
segment_analysis = customer_value.groupby("Customer_Segment", observed=True).agg(
    Customers=("Total_Net_Sales", "count"),
    Total_Net_Sales=("Total_Net_Sales", "sum")
)

# Calculate each segment's contribution to total Net Sales
segment_analysis["Revenue_Contribution_%"] = (
    segment_analysis["Total_Net_Sales"]
    / segment_analysis["Total_Net_Sales"].sum()
    * 100
)
print(segment_analysis)

# Sort customers from highest to lowest based on Total Net Sales
top_customers = (
    customer_value
    .sort_values("Total_Net_Sales", ascending=False)
    .head(10)
)
# Calculate total Net Sales generated by the top 10 customers
top_10_sales = top_customers["Total_Net_Sales"].sum()
# Calculate their contribution to overall Net Sales
top_10_contribution = (
    top_10_sales
    / customer_value["Total_Net_Sales"].sum()
    * 100
)
print("Top 10 Customers Sales:", top_10_sales)
print("Top 10 Customers Revenue Contribution %:", top_10_contribution)


# Group the dataset by Product
# This creates one group for every unique product
product_analysis = df.groupby("Product").agg(

    # Count unique orders for each product
    Total_Orders=("Order_ID", "nunique"),

    # Calculate total Net Sales generated by each product
    Net_Sales=("Net_Sales", "sum")
)
# Display the product-wise analysis
print(product_analysis)

# Calculate the Average Order Value (AOV) for each product
# AOV tells us how much Net Sales are generated per order on average
product_analysis["Product_AOV"] = (
    product_analysis["Net_Sales"]
    / product_analysis["Total_Orders"]
)
# Sort products from highest AOV to lowest AOV
product_aov = product_analysis.sort_values(
    "Product_AOV",
    ascending=False
)
# Display the product-wise AOV
print(product_aov)

# Calculate each product's contribution to total Net Sales
product_analysis["Sales_Contribution_%"] = (
    product_analysis["Net_Sales"]
    / product_analysis["Net_Sales"].sum()
    * 100
)
# Sort products from highest revenue contribution to lowest
product_contribution = product_analysis.sort_values(
    "Sales_Contribution_%",
    ascending=False
)
# Display the result
print(product_contribution)


# Sort products by Net Sales from highest to lowest
# Then select only the top 10 products
top_10_products_sales = (
    product_analysis
    .sort_values("Net_Sales", ascending=False)
    .head(10)
)
# Display the Top 10 products by Net Sales
print("\nTop 10 Products by Net Sales:")
print(top_10_products_sales)

# Sort products based on Total Orders from highest to lowest
# This identifies the products that are ordered most frequently
top_10_products_orders = (
    product_analysis
    .sort_values("Total_Orders", ascending=False)
    .head(10)
)
# Display the Top 10 products by order volume
print("\nTop 10 Products by Order Volume:")
print(top_10_products_orders)

# Sort products based on Product AOV from highest to lowest
# This identifies the products with the highest average order value
top_10_products_aov = (
    product_analysis
    .sort_values("Product_AOV", ascending=False)
    .head(10)
)
# Display the Top 10 products by AOV
print("\nTop 10 Products by AOV:")
print(top_10_products_aov)


# Group the data by both Category and Product
# This allows us to analyze products within each category
category_product_analysis = df.groupby(
    ["Category", "Product"]
).agg(

    # Count unique orders for each product
    Total_Orders=("Order_ID", "nunique"),

    # Calculate total Net Sales generated by each product
    Net_Sales=("Net_Sales", "sum")
)
# Display category-wise product performance
print("\nCategory-wise Product Performance:")
print(category_product_analysis)
# Convert the MultiIndex into normal columns
# This makes Category and Product easier to work with
top_products_by_category = (
    category_product_analysis
    .reset_index()

    # Sort products within each category by Net Sales
    .sort_values(
        ["Category", "Net_Sales"],
        ascending=[True, False]
    )

    # Select the top 5 products from each category
    .groupby("Category")
    .head(5)
)
# Display the Top 5 products from each category
print("\nTop 5 Products Within Each Category:")
print(top_products_by_category)


# Create a copy so that we do not accidentally modify our original analysis
category_product_contribution = category_product_analysis.reset_index().copy()
# Calculate the total Net Sales for each category
# transform("sum") keeps the category total on every product row
category_product_contribution["Category_Total_Sales"] = (
    category_product_contribution
    .groupby("Category")["Net_Sales"]
    .transform("sum")
)
# Calculate how much each product contributes to its own category's sales
category_product_contribution["Product_Contribution_%"] = (
    category_product_contribution["Net_Sales"]
    / category_product_contribution["Category_Total_Sales"]
    * 100
)
# Sort by Category and then by Product Contribution
category_product_contribution = category_product_contribution.sort_values(
    ["Category", "Product_Contribution_%"],
    ascending=[True, False]
)
# Display the result
print("\nProduct Contribution Within Each Category:")
print(category_product_contribution)


# Sort products by Net Sales from lowest to highest
# This helps us identify the lowest-performing products
bottom_10_products = (
    product_analysis
    .sort_values("Net_Sales", ascending=True)
    .head(10)
)
# Display the Bottom 10 products by Net Sales
print("\nBottom 10 Products by Net Sales:")
print(bottom_10_products)

# Find products that have high order volume
# but relatively low revenue contribution
high_volume_low_revenue = product_analysis[
    (product_analysis["Total_Orders"] >= product_analysis["Total_Orders"].quantile(0.75)) &
    (product_analysis["Sales_Contribution_%"] <= product_analysis["Sales_Contribution_%"].quantile(0.50))
]

# Sort them by order volume from highest to lowest
high_volume_low_revenue = high_volume_low_revenue.sort_values(
    "Total_Orders",
    ascending=False
)
# Display the products
print("\nHigh-Volume but Low-Revenue Products:")
print(high_volume_low_revenue)


# Count the number of orders placed by each customer in each category
customer_category_orders = pd.crosstab(
    df["Customer_ID"],
    df["Category"]
)
# Display the first few customers
print(customer_category_orders.head())

# Calculate total Net Sales generated by each customer in each category
customer_category_sales = (
    df.groupby(["Customer_ID", "Category"])["Net_Sales"]
      .sum()
      .unstack(fill_value=0)
)
# Display the first few customers
print(customer_category_sales.head())
# Find the category in which each customer generated the highest Net Sales
customer_preferred_category = customer_category_sales.idxmax(axis=1)
# Display the preferred category of each customer
print(customer_preferred_category.head())

# Count how many customers have each category as their preferred category
category_preference = customer_preferred_category.value_counts()
# Display the result
print(category_preference)
# Combine each customer's value segment with their preferred category
customer_preference_analysis = pd.DataFrame({
    "Customer_Segment": customer_value["Customer_Segment"],
    "Preferred_Category": customer_preferred_category
})
# Display the first few customers
print(customer_preference_analysis.head())

# Count customers for each combination of Customer Segment and Preferred Category
segment_category_preference = pd.crosstab(
    customer_preference_analysis["Customer_Segment"],
    customer_preference_analysis["Preferred_Category"]
)
# Display the result
print(segment_category_preference)

# Calculate the percentage distribution of preferred categories within each customer segment
segment_category_preference_pct = (
    segment_category_preference
    .div(segment_category_preference.sum(axis=1), axis=0)
    * 100
)
# Display the percentage distribution
print(segment_category_preference_pct.round(2))


# Count the number of different categories purchased by each customer
customer_category_diversity = df.groupby("Customer_ID")["Category"].nunique()
# Display the first few customers
print(customer_category_diversity.head())


# Count how many customers belong to each category-diversity level
category_diversity_distribution = customer_category_diversity.value_counts().sort_index()
# Display the distribution
print(category_diversity_distribution)


# Calculate the percentage of customers at each category-diversity level
category_diversity_pct = (
    category_diversity_distribution
    / category_diversity_distribution.sum()
    * 100
)
# Display the percentage distribution
print(category_diversity_pct.round(2))


# Calculate the average number of different categories purchased per customer
average_category_diversity = customer_category_diversity.mean()
# Display the result
print("Average Categories Purchased per Customer:", average_category_diversity)

#1️⃣2️⃣Customer Behavior Analysis
# Step 12.1 — Create a customer-level summary of orders and net sales
customer_behavior = df.groupby("Customer_ID").agg(
    Total_Orders=("Order_ID", "nunique"),
    Total_Net_Sales=("Net_Sales", "sum")
)
# Display the first few customers
print(customer_behavior.head())

# Step 12.2 — Calculate Average Order Value (AOV) for each customer
customer_behavior["Customer_AOV"] = (
    customer_behavior["Total_Net_Sales"]
    / customer_behavior["Total_Orders"]
)
# Display the first few customers
print(customer_behavior.head())

# Step 12.3 — Segment customers based on their total net sales
q25 = customer_behavior["Total_Net_Sales"].quantile(0.25)
q75 = customer_behavior["Total_Net_Sales"].quantile(0.75)

customer_behavior["Customer_Segment"] = pd.cut(
    customer_behavior["Total_Net_Sales"],
    bins=[-float("inf"), q25, q75, float("inf")],
    labels=["Low Value", "Medium Value", "High Value"]
)
# Display the first few customers with their segments
print(customer_behavior.head())

# Step 12.4 — Count the number of customers in each value segment
segment_counts = customer_behavior["Customer_Segment"].value_counts()
print(segment_counts)

# Step 12.5 — Calculate the percentage of customers in each value segment
segment_percentage = (
    segment_counts
    / segment_counts.sum()
    * 100
)
print(segment_percentage.round(2))

# Step 12.6 — Calculate total net sales generated by each customer segment
segment_sales = customer_behavior.groupby("Customer_Segment")["Total_Net_Sales"].sum()
print(segment_sales)

# Step 12.7 — Calculate each customer segment's contribution to total net sales
segment_sales_percentage = (
    segment_sales
    / segment_sales.sum()
    * 100
)
print(segment_sales_percentage.round(2))

# Step 12.8 — Create a combined customer segment performance summary
segment_summary = pd.DataFrame({
    "Customer_Count": segment_counts,
    "Customer_%": segment_percentage,
    "Total_Net_Sales": segment_sales,
    "Sales_Contribution_%": segment_sales_percentage
})
print(segment_summary.round(2))

# Step 12.9 — Find the top 10 customers by total net sales
top_customers = (
    customer_behavior
    .sort_values("Total_Net_Sales", ascending=False)
    .head(10)
)
print(top_customers)

# Step 12.10 — Calculate the sales contribution of the top 10 customers
top_10_sales = top_customers["Total_Net_Sales"].sum()

total_customer_sales = customer_behavior["Total_Net_Sales"].sum()

top_10_sales_percentage = (
    top_10_sales / total_customer_sales
) * 100
print("Top 10 Customers Sales:", top_10_sales)
print("Top 10 Sales Contribution (%):", round(top_10_sales_percentage, 2))

# Step 12.11 — Calculate average net sales per customer for each segment
segment_average_sales = (
    segment_sales / segment_counts
)
print(segment_average_sales.round(2))

# Step 12.12 — Analyze how many orders customers typically place
order_frequency = customer_behavior["Total_Orders"].value_counts().sort_index()
print(order_frequency)

# Step 12.13 — Calculate the average number of orders per customer
average_orders_per_customer = customer_behavior["Total_Orders"].mean()
print("Average Orders per Customer:", round(average_orders_per_customer, 2))

# Step 12.14 — Classify customers as one-time or repeat customers
customer_behavior["Customer_Type"] = (
    customer_behavior["Total_Orders"]
    .apply(lambda x: "One-time Customer" if x == 1 else "Repeat Customer")
)
print(customer_behavior["Customer_Type"].value_counts())

# Step 12.15 — Calculate the percentage of one-time and repeat customers
customer_type_percentage = (
    customer_behavior["Customer_Type"]
    .value_counts(normalize=True)
    * 100
)
print(customer_type_percentage.round(2))

# Step 12.16 — Calculate total net sales generated by each customer type
customer_type_sales = (
    customer_behavior
    .groupby("Customer_Type")["Total_Net_Sales"]
    .sum()
)
print(customer_type_sales)

# Step 12.17 — Calculate each customer type's contribution to total net sales
customer_type_sales_percentage = (
    customer_type_sales
    / customer_type_sales.sum()
    * 100
)
print(customer_type_sales_percentage.round(2))

# Step 12.18 — Calculate average sales generated per customer type
customer_type_average_sales = (
    customer_type_sales
    / customer_behavior["Customer_Type"].value_counts()
)
print(customer_type_average_sales.round(2))

# Step 12.19 — Calculate total sales generated by customers based on their order frequency
sales_by_order_frequency = (
    customer_behavior
    .groupby("Total_Orders")["Total_Net_Sales"]
    .sum()
    .sort_index()
)
print(sales_by_order_frequency)

# Step 12.20 — Calculate customer count and average sales for each order-frequency group
frequency_analysis = customer_behavior.groupby("Total_Orders").agg(
    Customer_Count=("Total_Net_Sales", "count"),
    Total_Net_Sales=("Total_Net_Sales", "sum")
)

frequency_analysis["Average_Sales_Per_Customer"] = (
    frequency_analysis["Total_Net_Sales"]
    / frequency_analysis["Customer_Count"]
)

print(frequency_analysis.round(2))

# Step 12.21 — Calculate sales contribution of each order-frequency group
frequency_analysis["Sales_Contribution_%"] = (
    frequency_analysis["Total_Net_Sales"]
    / frequency_analysis["Total_Net_Sales"].sum()
    * 100
)
print(frequency_analysis.round(2))

# Step 12.22 — Calculate combined sales contribution of customers with 3 to 7 orders
sales_3_to_7_orders = frequency_analysis.loc[
    3:7, "Total_Net_Sales"
].sum()

total_sales = frequency_analysis["Total_Net_Sales"].sum()

sales_3_to_7_percentage = (
    sales_3_to_7_orders / total_sales
) * 100

print("Sales from 3–7 Order Customers:", sales_3_to_7_orders)
print("Sales Contribution (%):", round(sales_3_to_7_percentage, 2))

# Step 12.23 — Find the order-frequency group with the highest total net sales
highest_sales_frequency = frequency_analysis[
    "Total_Net_Sales"
].idxmax()

highest_sales_amount = frequency_analysis.loc[
    highest_sales_frequency, "Total_Net_Sales"
]

highest_sales_contribution = frequency_analysis.loc[
    highest_sales_frequency, "Sales_Contribution_%"
]

print("Highest Sales Order Frequency:", highest_sales_frequency)
print("Total Net Sales:", highest_sales_amount)
print("Sales Contribution (%):", round(highest_sales_contribution, 2))

# Step 12.24 — Find the order-frequency group with the highest average sales per customer
highest_avg_frequency = frequency_analysis[
    "Average_Sales_Per_Customer"
].idxmax()

highest_avg_sales = frequency_analysis.loc[
    highest_avg_frequency, "Average_Sales_Per_Customer"
]

print("Highest Average Sales Order Frequency:", highest_avg_frequency)
print("Average Sales Per Customer:", round(highest_avg_sales, 2))

# Step 12.25 — Compare average sales of repeat and one-time customers
customer_type_avg_sales = (
    customer_behavior
    .groupby("Customer_Type")["Total_Net_Sales"]
    .mean()
)

repeat_customer_value = customer_type_avg_sales["Repeat Customer"]
one_time_customer_value = customer_type_avg_sales["One-time Customer"]

value_multiple = (
    repeat_customer_value / one_time_customer_value
)

print("Repeat Customer Average Sales:", round(repeat_customer_value, 2))
print("One-time Customer Average Sales:", round(one_time_customer_value, 2))
print("Repeat Customer Value Multiple:", round(value_multiple, 2), "x")

# Step 12.26 — Find the most common order frequency among customers
most_common_frequency = frequency_analysis[
    "Customer_Count"
].idxmax()

most_common_customer_count = frequency_analysis.loc[
    most_common_frequency, "Customer_Count"
]

print("Most Common Order Frequency:", most_common_frequency)
print("Number of Customers:", most_common_customer_count)

# Step 12.27 — Calculate customer percentage for each order-frequency group
frequency_analysis["Customer_%"] = (
    frequency_analysis["Customer_Count"]
    / frequency_analysis["Customer_Count"].sum()
    * 100
)

print(frequency_analysis.round(2))

# Step 12.28 — Calculate revenue efficiency of each order-frequency group
frequency_analysis["Revenue_Efficiency"] = (
    frequency_analysis["Sales_Contribution_%"]
    / frequency_analysis["Customer_%"]
)

print(frequency_analysis.round(2))

# Step 12.29 — Identify high-value customers with 5 or more orders
high_value_frequent_customers = customer_behavior[
    (customer_behavior["Customer_Segment"] == "High Value") &
    (customer_behavior["Total_Orders"] >= 5)
]

print(high_value_frequent_customers.head(10))
print("Number of High-Value Frequent Customers:",
      len(high_value_frequent_customers))


# Step 12.30 — Calculate sales contribution of high-value frequent customers
high_value_frequent_sales = (
    high_value_frequent_customers["Total_Net_Sales"].sum()
)

total_customer_sales = (
    customer_behavior["Total_Net_Sales"].sum()
)

high_value_frequent_sales_percentage = (
    high_value_frequent_sales
    / total_customer_sales
    * 100
)

print(
    "High-Value Frequent Customers Sales:",
    high_value_frequent_sales
)

print(
    "Sales Contribution (%):",
    round(high_value_frequent_sales_percentage, 2)
)

# Step 13.1 — Calculate the average number of orders placed by repeat customers
repeat_customers = customer_behavior[
    customer_behavior["Customer_Type"] == "Repeat Customer"
]
average_repeat_orders = repeat_customers["Total_Orders"].mean()

print("Average Orders per Repeat Customer:", round(average_repeat_orders, 2))

# Step 13.2 — Calculate the sales contribution of repeat customers
repeat_customer_sales = (
    repeat_customers["Total_Net_Sales"].sum()
)

total_customer_sales = (
    customer_behavior["Total_Net_Sales"].sum()
)

repeat_sales_percentage = (
    repeat_customer_sales
    / total_customer_sales
    * 100
)

print("Repeat Customer Sales:", repeat_customer_sales)
print("Repeat Customer Sales Contribution (%):",
      round(repeat_sales_percentage, 2))

# Step 13.3 — Compare average sales generated by repeat and one-time customers
customer_type_avg_sales = (
    customer_behavior
    .groupby("Customer_Type")["Total_Net_Sales"]
    .mean()
)

print(customer_type_avg_sales.round(2))

# Step 13.4 — Calculate how many times more valuable a repeat customer is
repeat_avg_sales = customer_type_avg_sales["Repeat Customer"]
one_time_avg_sales = customer_type_avg_sales["One-time Customer"]

repeat_value_multiple = (
    repeat_avg_sales / one_time_avg_sales
)

print(
    "Repeat Customer Value Multiple:",
    round(repeat_value_multiple, 2),
    "x"
)

# Step 13.5 — Analyze the order-frequency distribution of repeat customers
repeat_order_frequency = (
    repeat_customers["Total_Orders"]
    .value_counts()
    .sort_index()
)

print(repeat_order_frequency)

# Step 13.6 — Calculate the percentage of repeat customers with 5 or more orders
frequent_repeat_customers = repeat_customers[
    repeat_customers["Total_Orders"] >= 5
]

frequent_repeat_percentage = (
    len(frequent_repeat_customers)
    / len(repeat_customers)
    * 100
)

print("Repeat Customers with 5+ Orders:",
      len(frequent_repeat_customers))

print("Percentage of Repeat Customers with 5+ Orders:",
      round(frequent_repeat_percentage, 2), "%")

# Step 13.7 — Calculate total sales contribution of customers with 5 or more orders
frequent_repeat_sales = (
    frequent_repeat_customers["Total_Net_Sales"].sum()
)

total_customer_sales = (
    customer_behavior["Total_Net_Sales"].sum()
)

frequent_repeat_sales_percentage = (
    frequent_repeat_sales
    / total_customer_sales
    * 100
)

print("5+ Order Customers Sales:",
      frequent_repeat_sales)

print("5+ Order Customers Sales Contribution (%):",
      round(frequent_repeat_sales_percentage, 2), "%")

# Step 13.8 — Calculate average sales generated by customers with 5 or more orders
average_sales_5plus = (
    frequent_repeat_customers["Total_Net_Sales"].mean()
)

overall_average_sales = (
    customer_behavior["Total_Net_Sales"].mean()
)

print("Average Sales per 5+ Order Customer:",
      round(average_sales_5plus, 2))

print("Overall Average Sales per Customer:",
      round(overall_average_sales, 2))

# Step 13.9 — Calculate how many times more valuable a 5+ order customer is
five_plus_value_multiple = (
    average_sales_5plus / overall_average_sales
)

print(
    "5+ Order Customer Value Multiple:",
    round(five_plus_value_multiple, 2),
    "x"
)

# Step 13.10 — Calculate the percentage of total customers with 5 or more orders
five_plus_customer_percentage = (
    len(frequent_repeat_customers)
    / len(customer_behavior)
    * 100
)

print(
    "5+ Order Customers as % of Total Customers:",
    round(five_plus_customer_percentage, 2),
    "%"
)

# Step 13.11 — Calculate sales efficiency of 5+ order customers
five_plus_sales_efficiency = (
    frequent_repeat_sales_percentage
    / five_plus_customer_percentage
)

print(
    "5+ Order Customer Sales Efficiency:",
    round(five_plus_sales_efficiency, 2),
    "x"
)

# Step 13.12 — Create a customer retention summary table
retention_summary = pd.DataFrame({
    "Customer_Count": customer_behavior["Customer_Type"].value_counts(),
    "Customer_%": customer_behavior["Customer_Type"].value_counts(normalize=True) * 100,
    "Total_Net_Sales": customer_type_sales,
    "Sales_Contribution_%": customer_type_sales_percentage,
    "Average_Sales_Per_Customer": customer_type_avg_sales
})

print(retention_summary.round(2))

#1️⃣4️⃣ Time-Based Sales Analysis
# Step 14.1 — Extract Year and Month from Order_Date
df["Order_Year"] = df["Order_Date"].dt.year
df["Order_Month"] = df["Order_Date"].dt.month
df["Order_Month_Name"] = df["Order_Date"].dt.month_name()

print(df[["Order_Date", "Order_Year", "Order_Month", "Order_Month_Name"]].head())


# Step 14.2 — Calculate monthly order and sales performance
monthly_sales = df.groupby(
    ["Order_Year", "Order_Month"]
).agg(
    Total_Orders=("Order_ID", "nunique"),
    Total_Net_Sales=("Net_Sales", "sum")
)

print(monthly_sales)


# Step 14.3 — Calculate monthly Average Order Value
monthly_sales["Average_Order_Value"] = (
    monthly_sales["Total_Net_Sales"]
    / monthly_sales["Total_Orders"]
)

print(monthly_sales.round(2))


# Step 14.4 — Find the month with the highest total Net Sales
highest_sales_month = monthly_sales["Total_Net_Sales"].idxmax()
highest_sales_month_value = monthly_sales.loc[
    highest_sales_month,
    "Total_Net_Sales"
]

print("Highest Sales Month:", highest_sales_month)
print("Total Net Sales:", highest_sales_month_value)


# Step 14.5 — Find the month with the highest number of orders
highest_order_month = monthly_sales["Total_Orders"].idxmax()
highest_order_month_orders = monthly_sales.loc[
    highest_order_month,
    "Total_Orders"
]

print("Highest Order Volume Month:", highest_order_month)
print("Total Orders:", highest_order_month_orders)


# Step 14.6 — Calculate monthly sales contribution
monthly_sales["Sales_Contribution_%"] = (
    monthly_sales["Total_Net_Sales"]
    / monthly_sales["Total_Net_Sales"].sum()
    * 100
)

print(monthly_sales.round(2))


# Step 14.7 — Analyze sales performance by month name
month_name_sales = df.groupby("Order_Month_Name").agg(
    Total_Orders=("Order_ID", "nunique"),
    Total_Net_Sales=("Net_Sales", "sum")
)

month_name_sales["Average_Order_Value"] = (
    month_name_sales["Total_Net_Sales"]
    / month_name_sales["Total_Orders"]
)

print(month_name_sales.round(2))


# Step 14.8 — Analyze quarterly sales performance
df["Order_Quarter"] = df["Order_Date"].dt.quarter

quarterly_sales = df.groupby(
    ["Order_Year", "Order_Quarter"]
).agg(
    Total_Orders=("Order_ID", "nunique"),
    Total_Net_Sales=("Net_Sales", "sum")
)

quarterly_sales["Average_Order_Value"] = (
    quarterly_sales["Total_Net_Sales"]
    / quarterly_sales["Total_Orders"]
)

print(quarterly_sales.round(2))

# 1️⃣5️⃣Delivery Performance Analysis
# Step 15.1 — Calculate delivery time for orders with available delivery dates
df["Delivery_Days"] = (
    df["Delivery_Date"] - df["Order_Date"]
).dt.days

print(
    df[
        ["Order_ID", "Order_Date", "Delivery_Date", "Delivery_Days"]
    ].head()
)


# Step 15.2 — Analyze delivery performance for delivered orders
delivered_orders = df[
    (df["Order_Status"] == "Delivered") &
    (df["Delivery_Days"].notnull())
]

print(
    delivered_orders[
        ["Order_ID", "Order_Date", "Delivery_Date", "Delivery_Days"]
    ].head()
)


# Step 15.3 — Calculate average delivery time
average_delivery_days = delivered_orders["Delivery_Days"].mean()

print(
    "Average Delivery Time:",
    round(average_delivery_days, 2),
    "days"
)


# Step 15.4 — Find the fastest and slowest delivery times
fastest_delivery = delivered_orders["Delivery_Days"].min()
slowest_delivery = delivered_orders["Delivery_Days"].max()

print("Fastest Delivery:", fastest_delivery, "days")
print("Slowest Delivery:", slowest_delivery, "days")


# Step 15.5 — Analyze delivery time distribution
delivery_time_distribution = (
    delivered_orders["Delivery_Days"]
    .value_counts()
    .sort_index()
)

print(delivery_time_distribution)


# Step 15.6 — Calculate average delivery time by category
category_delivery = delivered_orders.groupby("Category").agg(
    Total_Orders=("Order_ID", "nunique"),
    Average_Delivery_Days=("Delivery_Days", "mean")
)

print(category_delivery.round(2))


# Step 15.7 — Calculate average delivery time by payment mode
payment_delivery = delivered_orders.groupby("Payment_Mode").agg(
    Total_Orders=("Order_ID", "nunique"),
    Average_Delivery_Days=("Delivery_Days", "mean")
)

print(payment_delivery.round(2))


# Step 15.8 — Identify orders with unusually long delivery times
long_delivery_orders = delivered_orders[
    delivered_orders["Delivery_Days"] >= 10
]

print(
    long_delivery_orders[
        [
            "Order_ID",
            "Customer_ID",
            "Category",
            "Order_Date",
            "Delivery_Date",
            "Delivery_Days"
        ]
    ].head(10)
)

print(
    "Orders with 10+ Delivery Days:",
    len(long_delivery_orders)
)

#1️⃣6️⃣ Payment Mode Analysis
# Step 16.1 — Analyze order volume by payment mode
payment_analysis = df.groupby("Payment_Mode").agg(
    Total_Orders=("Order_ID", "nunique"),
    Total_Net_Sales=("Net_Sales", "sum")
)

print(payment_analysis)


# Step 16.2 — Calculate payment mode percentage distribution
payment_analysis["Order_Contribution_%"] = (
    payment_analysis["Total_Orders"]
    / payment_analysis["Total_Orders"].sum()
    * 100
)

print(payment_analysis.round(2))


# Step 16.3 — Calculate Average Order Value by payment mode
payment_analysis["Average_Order_Value"] = (
    payment_analysis["Total_Net_Sales"]
    / payment_analysis["Total_Orders"]
)

print(payment_analysis.round(2))


# Step 16.4 — Calculate sales contribution by payment mode
payment_analysis["Sales_Contribution_%"] = (
    payment_analysis["Total_Net_Sales"]
    / payment_analysis["Total_Net_Sales"].sum()
    * 100
)

print(payment_analysis.round(2))


# Step 16.5 — Analyze order status by payment mode
payment_status_analysis = pd.crosstab(
    df["Payment_Mode"],
    df["Order_Status"]
)

print(payment_status_analysis)


# Step 16.6 — Calculate order status percentage within each payment mode
payment_status_percentage = (
    payment_status_analysis
    .div(payment_status_analysis.sum(axis=1), axis=0)
    * 100
)

print(payment_status_percentage.round(2))


# Step 16.7 — Find the most commonly used payment mode
most_common_payment_mode = (
    payment_analysis["Total_Orders"].idxmax()
)

most_common_payment_orders = (
    payment_analysis.loc[
        most_common_payment_mode,
        "Total_Orders"
    ]
)

print("Most Common Payment Mode:", most_common_payment_mode)
print("Total Orders:", most_common_payment_orders)


# Step 16.8 — Find the payment mode generating the highest Net Sales
highest_sales_payment_mode = (
    payment_analysis["Total_Net_Sales"].idxmax()
)

highest_payment_sales = (
    payment_analysis.loc[
        highest_sales_payment_mode,
        "Total_Net_Sales"
    ]
)

print(
    "Highest Sales Payment Mode:",
    highest_sales_payment_mode
)

print(
    "Total Net Sales:",
    highest_payment_sales
)

#1️⃣7️⃣ Final Business KPIs and Key Insights
# Step 17.1 — Create a final business KPI summary
final_kpis = {
    "Total Orders": df["Order_ID"].nunique(),
    "Unique Customers": df["Customer_ID"].nunique(),
    "Total Gross Sales": df["Gross_Sales"].sum(),
    "Total Discount": df["Discount_Amount"].sum(),
    "Total Net Sales": df["Net_Sales"].sum(),
    "Average Order Value": df["Net_Sales"].mean(),
    "Cancellation Rate (%)": (
        (df["Order_Status"] == "Cancelled").mean() * 100
    ),
    "Return Rate (%)": (
        (df["Order_Status"] == "Returned").mean() * 100
    )
}

final_kpi_summary = pd.Series(final_kpis)

print(final_kpi_summary.round(2))


# Step 17.2 — Calculate the percentage of revenue generated by delivered orders
delivered_sales = df.loc[
    df["Order_Status"] == "Delivered",
    "Net_Sales"
].sum()

total_sales = df["Net_Sales"].sum()

delivered_sales_percentage = (
    delivered_sales / total_sales
) * 100

print(
    "Delivered Sales Contribution (%):",
    round(delivered_sales_percentage, 2)
)


# Step 17.3 — Calculate revenue at risk from cancelled and returned orders
problem_orders_sales = df.loc[
    df["Order_Status"].isin(["Cancelled", "Returned"]),
    "Net_Sales"
].sum()

problem_sales_percentage = (
    problem_orders_sales / total_sales
) * 100

print(
    "Cancelled + Returned Sales:",
    problem_orders_sales
)

print(
    "Revenue Exposure (%):",
    round(problem_sales_percentage, 2)
)


# Step 17.4 — Identify the highest-value customer segment
highest_value_segment = segment_sales.idxmax()

highest_segment_sales = segment_sales.loc[
    highest_value_segment
]

highest_segment_contribution = segment_sales_percentage.loc[
    highest_value_segment
]

print(
    "Highest Revenue Customer Segment:",
    highest_value_segment
)

print(
    "Segment Sales:",
    highest_segment_sales
)

print(
    "Segment Contribution (%):",
    round(highest_segment_contribution, 2)
)


# Step 17.5 — Identify the highest-performing product
top_product = product_analysis["Net_Sales"].idxmax()
top_product_sales = product_analysis.loc[
    top_product,
    "Net_Sales"
]

print("Top Product:", top_product)
print("Top Product Net Sales:", top_product_sales)


# Step 17.6 — Identify the highest-performing category
top_category = category_sales["Net_Sales"].idxmax()
top_category_sales = category_sales.loc[
    top_category,
    "Net_Sales"
]

print("Top Category:", top_category)
print("Top Category Net Sales:", top_category_sales)


# Step 17.7 — Create a final summary of major business findings
business_summary = pd.DataFrame({
    "Metric": [
        "Total Orders",
        "Unique Customers",
        "Total Net Sales",
        "Average Order Value",
        "Cancellation Rate",
        "Return Rate",
        "Average Delivery Time",
        "Top Product",
        "Top Category",
        "Top Payment Mode",
        "Highest Customer Segment"
    ],
    "Value": [
        df["Order_ID"].nunique(),
        df["Customer_ID"].nunique(),
        df["Net_Sales"].sum(),
        df["Net_Sales"].mean(),
        (df["Order_Status"] == "Cancelled").mean() * 100,
        (df["Order_Status"] == "Returned").mean() * 100,
        delivered_orders["Delivery_Days"].mean(),
        top_product,
        top_category,
        most_common_payment_mode,
        highest_value_segment
    ]
})

print(business_summary)


# Step 17.8 — Save the cleaned and analyzed dataset for further analysis
df.to_csv(
    "ecommerce_sales_cleaned.csv",
    index=False
)

print("Cleaned dataset saved successfully.")