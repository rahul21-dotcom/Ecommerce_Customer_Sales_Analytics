
-- ============================================================
-- STEP 1: SELECT THE DATABASE
-- Choose the existing E-Commerce Analytics database
-- ============================================================

USE ecommerce_analytics;


-- ============================================================
-- STEP 2: CHECK THE IMPORTED DATA
-- Verify total rows, unique orders, and preview the dataset
-- ============================================================

SELECT COUNT(*) AS total_records
FROM ecommerce_sales_raw;

SELECT COUNT(DISTINCT Order_ID) AS unique_order_ids
FROM ecommerce_sales_raw;

SELECT *
FROM ecommerce_sales_raw
LIMIT 10;


-- ============================================================
-- STEP 3: CHECK THE TABLE STRUCTURE
-- Inspect column names, data types, and table definition
-- ============================================================

DESCRIBE ecommerce_sales_raw;

SHOW CREATE TABLE ecommerce_sales_raw;


-- ============================================================
-- STEP 4: CHECK DUPLICATE ORDER IDs
-- Find Order_ID values that occur more than once
-- ============================================================

SELECT
    Order_ID,
    COUNT(*) AS occurrences
FROM ecommerce_sales_raw
GROUP BY Order_ID
HAVING COUNT(*) > 1
ORDER BY occurrences DESC;


-- ============================================================
-- STEP 5: CHECK EXACT DUPLICATE ROWS
-- Identify rows that match across all 18 columns
-- ============================================================

SELECT
    Order_ID,
    Customer_ID,
    Customer_Name,
    Gender,
    Age,
    City,
    State,
    Product,
    Category,
    Sub_Category,
    Quantity,
    Unit_Price,
    Discount,
    Order_Date,
    Delivery_Date,
    Payment_Mode,
    Order_Status,
    Rating,
    COUNT(*) AS occurrences
FROM ecommerce_sales_raw
GROUP BY
    Order_ID,
    Customer_ID,
    Customer_Name,
    Gender,
    Age,
    City,
    State,
    Product,
    Category,
    Sub_Category,
    Quantity,
    Unit_Price,
    Discount,
    Order_Date,
    Delivery_Date,
    Payment_Mode,
    Order_Status,
    Rating
HAVING COUNT(*) > 1
ORDER BY occurrences DESC;


-- ============================================================
-- STEP 6: CHECK MISSING VALUES
-- Count NULL values in each important column
-- ============================================================

SELECT
    COUNT(*) AS total_records,
    SUM(Order_ID IS NULL) AS missing_order_id,
    SUM(Customer_ID IS NULL) AS missing_customer_id,
    SUM(Customer_Name IS NULL) AS missing_customer_name,
    SUM(Gender IS NULL) AS missing_gender,
    SUM(Age IS NULL) AS missing_age,
    SUM(City IS NULL) AS missing_city,
    SUM(State IS NULL) AS missing_state,
    SUM(Product IS NULL) AS missing_product,
    SUM(Category IS NULL) AS missing_category,
    SUM(Sub_Category IS NULL) AS missing_sub_category,
    SUM(Quantity IS NULL) AS missing_quantity,
    SUM(Unit_Price IS NULL) AS missing_unit_price,
    SUM(Discount IS NULL) AS missing_discount,
    SUM(Order_Date IS NULL) AS missing_order_date,
    SUM(Delivery_Date IS NULL) AS missing_delivery_date,
    SUM(Payment_Mode IS NULL) AS missing_payment_mode,
    SUM(Order_Status IS NULL) AS missing_order_status,
    SUM(Rating IS NULL) AS missing_rating
FROM ecommerce_sales_raw;


-- ============================================================
-- STEP 7: CHECK UNIQUE VALUES IN CATEGORICAL COLUMNS
-- Understand the categories and labels present in the data
-- ============================================================

SELECT DISTINCT Gender
FROM ecommerce_sales_raw
ORDER BY Gender;

SELECT DISTINCT Category
FROM ecommerce_sales_raw
ORDER BY Category;

SELECT DISTINCT Sub_Category
FROM ecommerce_sales_raw
ORDER BY Sub_Category;

SELECT DISTINCT Order_Status
FROM ecommerce_sales_raw
ORDER BY Order_Status;

SELECT DISTINCT Payment_Mode
FROM ecommerce_sales_raw
ORDER BY Payment_Mode;

SELECT DISTINCT State
FROM ecommerce_sales_raw
ORDER BY State;


-- ============================================================
-- STEP 8: CHECK INVALID NUMERIC VALUES
-- Look for impossible ages, quantities, prices, discounts, ratings
-- ============================================================

SELECT *
FROM ecommerce_sales_raw
WHERE
    Age < 0
    OR Quantity <= 0
    OR Unit_Price < 0
    OR Discount < 0
    OR Rating < 0
    OR Rating > 5;

SELECT
    MIN(Age) AS minimum_age,
    MAX(Age) AS maximum_age,
    MIN(Quantity) AS minimum_quantity,
    MAX(Quantity) AS maximum_quantity,
    MIN(Unit_Price) AS minimum_unit_price,
    MAX(Unit_Price) AS maximum_unit_price,
    MIN(Discount) AS minimum_discount,
    MAX(Discount) AS maximum_discount,
    MIN(Rating) AS minimum_rating,
    MAX(Rating) AS maximum_rating
FROM ecommerce_sales_raw;


-- ============================================================
-- STEP 9: CHECK DATE RANGE AND DATE CONSISTENCY
-- Find the reporting period and potentially incorrect dates
-- ============================================================

SELECT
    MIN(Order_Date) AS first_order_date,
    MAX(Order_Date) AS last_order_date,
    MIN(Delivery_Date) AS first_delivery_date,
    MAX(Delivery_Date) AS last_delivery_date
FROM ecommerce_sales_raw;

SELECT *
FROM ecommerce_sales_raw
WHERE
    Order_Date IS NOT NULL
    AND Delivery_Date IS NOT NULL
    AND Delivery_Date < Order_Date;

SELECT
    Order_Status,
    COUNT(*) AS total_orders,
    SUM(Delivery_Date IS NULL) AS missing_delivery_dates
FROM ecommerce_sales_raw
GROUP BY Order_Status
ORDER BY total_orders DESC;


-- ============================================================
-- STEP 10: CHECK ORDER STATUS DISTRIBUTION
-- Count orders and calculate their percentage by status
-- ============================================================

SELECT
    Order_Status,
    COUNT(*) AS total_orders,
    ROUND(
        COUNT(*) * 100.0 /
        NULLIF((SELECT COUNT(*) FROM ecommerce_sales_raw), 0),
        2
    ) AS percentage_of_records
FROM ecommerce_sales_raw
GROUP BY Order_Status
ORDER BY total_orders DESC;


-- ============================================================
-- STEP 11: CREATE A SALES ANALYSIS VIEW
-- Calculate gross sales, discount amount, and net sales
-- Assumption: Discount is a rate such as 0.10 or 10
-- Values greater than 1 are interpreted as percentages
-- ============================================================

CREATE OR REPLACE VIEW vw_ecommerce_sales_analysis AS
SELECT
    Order_ID,
    Customer_ID,
    Customer_Name,
    Gender,
    Age,
    City,
    State,
    Product,
    Category,
    Sub_Category,
    Quantity,
    Unit_Price,
    Discount,
    Order_Date,
    Delivery_Date,
    Payment_Mode,
    Order_Status,
    Rating,
    COALESCE(Quantity, 0) * COALESCE(Unit_Price, 0)
        AS Gross_Sales,
    CASE
        WHEN Discount IS NULL THEN 0
        WHEN Discount > 1 THEN Discount / 100.0
        ELSE Discount
    END AS Discount_Rate,
    COALESCE(Quantity, 0) * COALESCE(Unit_Price, 0) *
    CASE
        WHEN Discount IS NULL THEN 0
        WHEN Discount > 1 THEN Discount / 100.0
        ELSE Discount
    END AS Discount_Amount,
    COALESCE(Quantity, 0) * COALESCE(Unit_Price, 0) *
    (1 - CASE
        WHEN Discount IS NULL THEN 0
        WHEN Discount > 1 THEN Discount / 100.0
        ELSE Discount
    END) AS Net_Sales
FROM ecommerce_sales_raw;


-- ============================================================
-- STEP 12: CHECK OVERALL BUSINESS KPIs
-- Calculate total records, sales, discounts, and average order value
-- ============================================================

SELECT
    COUNT(*) AS total_records,
    COUNT(DISTINCT Order_ID) AS unique_orders,
    COUNT(DISTINCT Customer_ID) AS unique_customers,
    ROUND(SUM(Gross_Sales), 2) AS total_gross_sales,
    ROUND(SUM(Discount_Amount), 2) AS total_discount_amount,
    ROUND(SUM(Net_Sales), 2) AS total_net_sales,
    ROUND(AVG(Net_Sales), 2) AS average_net_sales_per_record
FROM vw_ecommerce_sales_analysis;

SELECT
    ROUND(
        SUM(Net_Sales) /
        NULLIF(COUNT(DISTINCT Order_ID), 0),
        2
    ) AS average_net_sales_per_order
FROM vw_ecommerce_sales_analysis;


-- ============================================================
-- STEP 13: ANALYZE SALES BY ORDER STATUS
-- Compare sales, records, and average sales across statuses
-- ============================================================

SELECT
    Order_Status,
    COUNT(*) AS total_records,
    COUNT(DISTINCT Order_ID) AS unique_orders,
    ROUND(SUM(Gross_Sales), 2) AS gross_sales,
    ROUND(SUM(Discount_Amount), 2) AS discount_amount,
    ROUND(SUM(Net_Sales), 2) AS net_sales,
    ROUND(AVG(Net_Sales), 2) AS average_net_sales
FROM vw_ecommerce_sales_analysis
GROUP BY Order_Status
ORDER BY net_sales DESC;


-- ============================================================
-- STEP 14: ANALYZE SALES BY CATEGORY
-- Identify the highest-revenue product categories
-- ============================================================

SELECT
    Category,
    COUNT(*) AS total_records,
    SUM(Quantity) AS units_sold,
    ROUND(SUM(Net_Sales), 2) AS net_sales,
    ROUND(AVG(Net_Sales), 2) AS average_net_sales,
    ROUND(
        SUM(Net_Sales) * 100.0 /
        NULLIF(
            (SELECT SUM(Net_Sales)
             FROM vw_ecommerce_sales_analysis),
            0
        ),
        2
    ) AS sales_contribution_percentage
FROM vw_ecommerce_sales_analysis
GROUP BY Category
ORDER BY net_sales DESC;


-- ============================================================
-- STEP 15: ANALYZE SALES BY SUB-CATEGORY
-- Discover which sub-categories contribute the most revenue
-- ============================================================

SELECT
    Category,
    Sub_Category,
    COUNT(*) AS total_records,
    SUM(Quantity) AS units_sold,
    ROUND(SUM(Net_Sales), 2) AS net_sales
FROM vw_ecommerce_sales_analysis
GROUP BY Category, Sub_Category
ORDER BY net_sales DESC;


-- ============================================================
-- STEP 16: IDENTIFY TOP-SELLING PRODUCTS
-- Rank products by net sales and quantity sold
-- ============================================================

SELECT
    Product,
    Category,
    Sub_Category,
    SUM(Quantity) AS units_sold,
    COUNT(*) AS total_records,
    ROUND(SUM(Net_Sales), 2) AS net_sales
FROM vw_ecommerce_sales_analysis
GROUP BY Product, Category, Sub_Category
ORDER BY net_sales DESC
LIMIT 10;


-- ============================================================
-- STEP 17: IDENTIFY LOW-REVENUE PRODUCTS
-- Find products with the lowest total net sales
-- ============================================================

SELECT
    Product,
    Category,
    SUM(Quantity) AS units_sold,
    ROUND(SUM(Net_Sales), 2) AS net_sales
FROM vw_ecommerce_sales_analysis
GROUP BY Product, Category
ORDER BY net_sales ASC
LIMIT 10;


-- ============================================================
-- STEP 18: ANALYZE SALES BY CUSTOMER
-- Find each customer's order count and total net sales
-- ============================================================

SELECT
    Customer_ID,
    MAX(Customer_Name) AS Customer_Name,
    COUNT(DISTINCT Order_ID) AS total_orders,
    ROUND(SUM(Net_Sales), 2) AS total_net_sales,
    ROUND(AVG(Net_Sales), 2) AS average_sales_per_record
FROM vw_ecommerce_sales_analysis
GROUP BY Customer_ID
ORDER BY total_net_sales DESC
LIMIT 20;


-- ============================================================
-- STEP 19: SEGMENT CUSTOMERS BY SPENDING
-- Classify customers into Low, Medium, and High spending groups
-- Uses customer-level net sales and NTILE(4) quartiles
-- ============================================================

WITH customer_sales AS (
    SELECT
        Customer_ID,
        SUM(Net_Sales) AS total_net_sales
    FROM vw_ecommerce_sales_analysis
    GROUP BY Customer_ID
),
customer_quartiles AS (
    SELECT
        Customer_ID,
        total_net_sales,
        NTILE(4) OVER (ORDER BY total_net_sales) AS spending_quartile
    FROM customer_sales
)
SELECT
    CASE
        WHEN spending_quartile = 1 THEN 'Low'
        WHEN spending_quartile IN (2, 3) THEN 'Medium'
        ELSE 'High'
    END AS Customer_Segment,
    COUNT(*) AS total_customers,
    ROUND(AVG(total_net_sales), 2) AS average_customer_sales,
    ROUND(SUM(total_net_sales), 2) AS segment_net_sales
FROM customer_quartiles
GROUP BY Customer_Segment
ORDER BY segment_net_sales DESC;


-- ============================================================
-- STEP 20: IDENTIFY REPEAT AND ONE-TIME CUSTOMERS
-- Measure customer retention through order frequency
-- ============================================================

WITH customer_orders AS (
    SELECT
        Customer_ID,
        COUNT(DISTINCT Order_ID) AS total_orders
    FROM vw_ecommerce_sales_analysis
    GROUP BY Customer_ID
)
SELECT
    CASE
        WHEN total_orders = 1 THEN 'One-time Customer'
        ELSE 'Repeat Customer'
    END AS Customer_Type,
    COUNT(*) AS total_customers,
    ROUND(
        COUNT(*) * 100.0 /
        NULLIF((SELECT COUNT(*) FROM customer_orders), 0),
        2
    ) AS percentage_of_customers
FROM customer_orders
GROUP BY Customer_Type;


-- ============================================================
-- STEP 21: ANALYZE SALES BY GENDER
-- Compare customer records, orders, and net sales by gender
-- ============================================================

SELECT
    Gender,
    COUNT(*) AS total_records,
    COUNT(DISTINCT Customer_ID) AS unique_customers,
    COUNT(DISTINCT Order_ID) AS unique_orders,
    ROUND(SUM(Net_Sales), 2) AS net_sales
FROM vw_ecommerce_sales_analysis
GROUP BY Gender
ORDER BY net_sales DESC;


-- ============================================================
-- STEP 22: ANALYZE SALES BY AGE GROUP
-- Understand spending patterns across customer age groups
-- ============================================================

SELECT
    CASE
        WHEN Age < 18 THEN 'Under 18'
        WHEN Age BETWEEN 18 AND 25 THEN '18-25'
        WHEN Age BETWEEN 26 AND 35 THEN '26-35'
        WHEN Age BETWEEN 36 AND 45 THEN '36-45'
        WHEN Age BETWEEN 46 AND 60 THEN '46-60'
        WHEN Age > 60 THEN 'Above 60'
        ELSE 'Unknown'
    END AS Age_Group,
    COUNT(DISTINCT Customer_ID) AS unique_customers,
    COUNT(DISTINCT Order_ID) AS unique_orders,
    ROUND(SUM(Net_Sales), 2) AS net_sales
FROM vw_ecommerce_sales_analysis
GROUP BY Age_Group
ORDER BY net_sales DESC;


-- ============================================================
-- STEP 23: ANALYZE SALES BY CITY
-- Identify cities generating the most net sales
-- ============================================================

SELECT
    City,
    State,
    COUNT(DISTINCT Order_ID) AS unique_orders,
    COUNT(DISTINCT Customer_ID) AS unique_customers,
    ROUND(SUM(Net_Sales), 2) AS net_sales
FROM vw_ecommerce_sales_analysis
GROUP BY City, State
ORDER BY net_sales DESC
LIMIT 20;


-- ============================================================
-- STEP 24: ANALYZE SALES BY STATE
-- Compare geographical performance across states
-- ============================================================

SELECT
    State,
    COUNT(DISTINCT Order_ID) AS unique_orders,
    COUNT(DISTINCT Customer_ID) AS unique_customers,
    ROUND(SUM(Net_Sales), 2) AS net_sales
FROM vw_ecommerce_sales_analysis
GROUP BY State
ORDER BY net_sales DESC;


-- ============================================================
-- STEP 25: ANALYZE PAYMENT METHODS
-- Find the most commonly used payment methods
-- ============================================================

SELECT
    Payment_Mode,
    COUNT(*) AS total_records,
    COUNT(DISTINCT Order_ID) AS unique_orders,
    ROUND(SUM(Net_Sales), 2) AS net_sales
FROM vw_ecommerce_sales_analysis
GROUP BY Payment_Mode
ORDER BY unique_orders DESC;


-- ============================================================
-- STEP 26: ANALYZE MONTHLY SALES TRENDS
-- Track monthly revenue, order volume, and average sales
-- ============================================================

SELECT
    DATE_FORMAT(Order_Date, '%Y-%m') AS sales_month,
    COUNT(DISTINCT Order_ID) AS unique_orders,
    SUM(Quantity) AS units_sold,
    ROUND(SUM(Net_Sales), 2) AS net_sales,
    ROUND(
        SUM(Net_Sales) /
        NULLIF(COUNT(DISTINCT Order_ID), 0),
        2
    ) AS average_net_sales_per_order
FROM vw_ecommerce_sales_analysis
WHERE Order_Date IS NOT NULL
GROUP BY DATE_FORMAT(Order_Date, '%Y-%m')
ORDER BY sales_month;


-- ============================================================
-- STEP 27: ANALYZE YEARLY SALES TRENDS
-- Compare revenue and order volume across years
-- ============================================================

SELECT
    YEAR(Order_Date) AS sales_year,
    COUNT(DISTINCT Order_ID) AS unique_orders,
    SUM(Quantity) AS units_sold,
    ROUND(SUM(Net_Sales), 2) AS net_sales
FROM vw_ecommerce_sales_analysis
WHERE Order_Date IS NOT NULL
GROUP BY YEAR(Order_Date)
ORDER BY sales_year;


-- ============================================================
-- STEP 28: ANALYZE WEEKDAY SALES
-- Find which days of the week generate the most sales
-- ============================================================

SELECT
    DAYNAME(Order_Date) AS weekday_name,
    DAYOFWEEK(Order_Date) AS weekday_number,
    COUNT(DISTINCT Order_ID) AS unique_orders,
    ROUND(SUM(Net_Sales), 2) AS net_sales
FROM vw_ecommerce_sales_analysis
WHERE Order_Date IS NOT NULL
GROUP BY
    DAYNAME(Order_Date),
    DAYOFWEEK(Order_Date)
ORDER BY weekday_number;


-- ============================================================
-- STEP 29: ANALYZE CUSTOMER RATINGS
-- Review rating distribution and average rating by category
-- ============================================================

SELECT
    Rating,
    COUNT(*) AS rating_count
FROM ecommerce_sales_raw
WHERE Rating IS NOT NULL
GROUP BY Rating
ORDER BY Rating DESC;

SELECT
    Category,
    COUNT(Rating) AS rated_records,
    ROUND(AVG(Rating), 2) AS average_rating
FROM ecommerce_sales_raw
GROUP BY Category
ORDER BY average_rating DESC;


-- ============================================================
-- STEP 30: FIND LOW-RATED PRODUCTS
-- Identify products with lower average customer ratings
-- ============================================================

SELECT
    Product,
    Category,
    COUNT(Rating) AS number_of_ratings,
    ROUND(AVG(Rating), 2) AS average_rating
FROM ecommerce_sales_raw
WHERE Rating IS NOT NULL
GROUP BY Product, Category
HAVING COUNT(Rating) >= 5
ORDER BY average_rating ASC, number_of_ratings DESC
LIMIT 10;


-- ============================================================
-- STEP 31: ANALYZE DELIVERY TIME
-- Calculate average delivery days for delivered orders
-- ============================================================

SELECT
    COUNT(*) AS delivered_records_with_dates,
    ROUND(
        AVG(DATEDIFF(Delivery_Date, Order_Date)),
        2
    ) AS average_delivery_days,
    MIN(DATEDIFF(Delivery_Date, Order_Date)) AS minimum_delivery_days,
    MAX(DATEDIFF(Delivery_Date, Order_Date)) AS maximum_delivery_days
FROM ecommerce_sales_raw
WHERE
    Order_Status = 'Delivered'
    AND Order_Date IS NOT NULL
    AND Delivery_Date IS NOT NULL;


-- ============================================================
-- STEP 32: CHECK DELIVERY TIME BY CATEGORY
-- Compare average delivery time for delivered products
-- ============================================================

SELECT
    Category,
    COUNT(*) AS delivered_records_with_dates,
    ROUND(
        AVG(DATEDIFF(Delivery_Date, Order_Date)),
        2
    ) AS average_delivery_days
FROM ecommerce_sales_raw
WHERE
    Order_Status = 'Delivered'
    AND Order_Date IS NOT NULL
    AND Delivery_Date IS NOT NULL
GROUP BY Category
ORDER BY average_delivery_days ASC;


-- ============================================================
-- STEP 33: CALCULATE CANCELLATION AND RETURN RATES
-- Measure cancelled and returned records against all records
-- ============================================================

SELECT
    COUNT(*) AS total_records,
    SUM(Order_Status = 'Delivered') AS delivered_records,
    SUM(Order_Status = 'Cancelled') AS cancelled_records,
    SUM(Order_Status = 'Returned') AS returned_records,
    ROUND(
        SUM(Order_Status = 'Cancelled') * 100.0 /
        NULLIF(COUNT(*), 0),
        2
    ) AS cancellation_percentage,
    ROUND(
        SUM(Order_Status = 'Returned') * 100.0 /
        NULLIF(COUNT(*), 0),
        2
    ) AS return_percentage
FROM ecommerce_sales_raw;


-- ============================================================
-- STEP 34: FIND PRODUCTS WITH HIGH CANCELLATION COUNTS
-- Identify products frequently appearing in cancelled records
-- ============================================================

SELECT
    Product,
    Category,
    COUNT(*) AS cancelled_records
FROM ecommerce_sales_raw
WHERE Order_Status = 'Cancelled'
GROUP BY Product, Category
ORDER BY cancelled_records DESC
LIMIT 10;


-- ============================================================
-- STEP 35: CHECK DISCOUNT IMPACT
-- Compare average discount rate and net sales by category
-- ============================================================

SELECT
    Category,
    ROUND(AVG(
        CASE
            WHEN Discount IS NULL THEN NULL
            WHEN Discount > 1 THEN Discount / 100.0
            ELSE Discount
        END
    ) * 100, 2) AS average_discount_percentage,
    ROUND(SUM(Gross_Sales), 2) AS gross_sales,
    ROUND(SUM(Discount_Amount), 2) AS total_discount_amount,
    ROUND(SUM(Net_Sales), 2) AS net_sales
FROM vw_ecommerce_sales_analysis
GROUP BY Category
ORDER BY net_sales DESC;


-- ============================================================
-- STEP 36: FIND HIGH-ORDER, LOW-REVENUE PRODUCTS
-- Find products with many records but comparatively low revenue
-- ============================================================

SELECT
    Product,
    Category,
    COUNT(DISTINCT Order_ID) AS unique_orders,
    SUM(Quantity) AS units_sold,
    ROUND(SUM(Net_Sales), 2) AS net_sales,
    ROUND(
        SUM(Net_Sales) /
        NULLIF(COUNT(DISTINCT Order_ID), 0),
        2
    ) AS average_net_sales_per_order
FROM vw_ecommerce_sales_analysis
GROUP BY Product, Category
HAVING COUNT(DISTINCT Order_ID) >= 5
ORDER BY average_net_sales_per_order ASC
LIMIT 10;


-- ============================================================
-- STEP 37: CREATE A FINAL KPI SUMMARY
-- Prepare a compact summary for reporting and dashboards
-- ============================================================

SELECT
    COUNT(*) AS total_records,
    COUNT(DISTINCT Order_ID) AS unique_orders,
    COUNT(DISTINCT Customer_ID) AS unique_customers,
    ROUND(SUM(Gross_Sales), 2) AS gross_sales,
    ROUND(SUM(Discount_Amount), 2) AS discount_amount,
    ROUND(SUM(Net_Sales), 2) AS net_sales,
    ROUND(
        SUM(Net_Sales) /
        NULLIF(COUNT(DISTINCT Order_ID), 0),
        2
    ) AS average_net_sales_per_order,
    ROUND(
        SUM(Order_Status = 'Delivered') * 100.0 /
        NULLIF(COUNT(*), 0),
        2
    ) AS delivered_percentage,
    ROUND(
        SUM(Order_Status = 'Cancelled') * 100.0 /
        NULLIF(COUNT(*), 0),
        2
    ) AS cancelled_percentage,
    ROUND(
        SUM(Order_Status = 'Returned') * 100.0 /
        NULLIF(COUNT(*), 0),
        2
    ) AS returned_percentage
FROM vw_ecommerce_sales_analysis;


-- ============================================================
-- STEP 38: VERIFY THE ANALYSIS VIEW
-- Confirm that the calculated sales fields are available
-- ============================================================

SELECT *
FROM vw_ecommerce_sales_analysis
LIMIT 10;


-- ============================================================
-- STEP 39: CHECK ALL TABLES AND VIEWS
-- Review database objects after completing the analysis
-- ============================================================

SHOW FULL TABLES IN ecommerce_analytics;


-- ============================================================
-- STEP 40: FINAL DATASET RECORD COUNT
-- Confirm the original imported table remains intact
-- ============================================================

SELECT COUNT(*) AS final_raw_record_count
FROM ecommerce_sales_raw;

