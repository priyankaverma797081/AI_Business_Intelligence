import pandas as pd
import mysql.connector
from mysql.connector import Error
from getpass import getpass

# ==========================================
# 1. DATABASE CONFIGURATION
# ==========================================

DB_HOST = "localhost"
DB_USER = "root"
DB_NAME = "ai_business_intelligence"

print("=" * 55)
print("AI BUSINESS INTELLIGENCE PROJECT")
print("MYSQL DATABASE INTEGRATION")
print("=" * 55)

# Ask for MySQL password securely
DB_PASSWORD = getpass("Enter your MySQL root password: ")

connection = None
cursor = None

try:
    # ==========================================
    # 2. CONNECT TO MYSQL SERVER
    # ==========================================

    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD
    )

    if connection.is_connected():
        print("\nConnected to MySQL Server successfully!")

    cursor = connection.cursor()

    # ==========================================
    # 3. CREATE DATABASE
    # ==========================================

    cursor.execute(
        f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"
    )

    cursor.execute(f"USE {DB_NAME}")

    print(f"Database '{DB_NAME}' is ready.")

    # ==========================================
    # 4. CREATE SALES TABLE
    # ==========================================

    create_table_query = """
    CREATE TABLE IF NOT EXISTS sales (
        Order_ID VARCHAR(30) PRIMARY KEY,
        Order_Date DATE NOT NULL,
        Customer_ID VARCHAR(30),
        Product VARCHAR(100),
        Category VARCHAR(100),
        Region VARCHAR(50),
        Quantity INT,
        Unit_Price DECIMAL(12, 2),
        Discount_Pct DECIMAL(5, 4),
        Total_Sales DECIMAL(14, 2)
    )
    """

    cursor.execute(create_table_query)
    print("Sales table is ready.")

    # ==========================================
    # 5. LOAD CLEANED CSV DATA
    # ==========================================

    df = pd.read_csv("data/cleaned_sales_data.csv")

    df["Order_Date"] = pd.to_datetime(
        df["Order_Date"], errors="raise"
    )

    print("\nCSV data loaded successfully.")
    print("Rows in CSV:", len(df))

    # ==========================================
    # 6. PREPARE DATA FOR MYSQL
    # ==========================================

    columns = [
        "Order_ID",
        "Order_Date",
        "Customer_ID",
        "Product",
        "Category",
        "Region",
        "Quantity",
        "Unit_Price",
        "Discount_Pct",
        "Total_Sales"
    ]

    df = df[columns]

    # Convert pandas rows into Python tuples
    records = []

    for row in df.itertuples(index=False, name=None):
        records.append((
            str(row[0]),
            row[1].date(),
            str(row[2]),
            str(row[3]),
            str(row[4]),
            str(row[5]),
            int(row[6]),
            float(row[7]),
            float(row[8]),
            float(row[9])
        ))

    # ==========================================
    # 7. INSERT DATA INTO MYSQL
    # ==========================================

    insert_query = """
    INSERT INTO sales (
        Order_ID, Order_Date, Customer_ID, Product,
        Category, Region, Quantity, Unit_Price,
        Discount_Pct, Total_Sales
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        Order_Date = VALUES(Order_Date),
        Customer_ID = VALUES(Customer_ID),
        Product = VALUES(Product),
        Category = VALUES(Category),
        Region = VALUES(Region),
        Quantity = VALUES(Quantity),
        Unit_Price = VALUES(Unit_Price),
        Discount_Pct = VALUES(Discount_Pct),
        Total_Sales = VALUES(Total_Sales)
    """

    cursor.executemany(insert_query, records)
    connection.commit()

    print("\nData inserted/updated successfully!")
    print("Rows processed:", cursor.rowcount)

    # ==========================================
    # 8. VERIFY DATABASE DATA
    # ==========================================

    cursor.execute("SELECT COUNT(*) FROM sales")
    total_rows = cursor.fetchone()[0]

    cursor.execute("""
        SELECT
            COUNT(DISTINCT Customer_ID),
            SUM(Total_Sales)
        FROM sales
    """)

    total_customers, total_sales = cursor.fetchone()

    print("\n--- DATABASE VERIFICATION ---")
    print("Total rows in MySQL:", total_rows)
    print("Unique customers:", total_customers)
    print(f"Total sales: Rs. {total_sales:,.2f}")

    # ==========================================
    # 9. DISPLAY SAMPLE RECORDS
    # ==========================================

    cursor.execute("""
        SELECT Order_ID, Order_Date, Product, Total_Sales
        FROM sales
        LIMIT 5
    """)

    print("\n--- SAMPLE DATABASE RECORDS ---")

    for record in cursor.fetchall():
        print(record)

    print("\n" + "=" * 55)
    print("MYSQL INTEGRATION COMPLETED SUCCESSFULLY")
    print("=" * 55)

except Error as e:
    print("\nMySQL Error:", e)
    if connection and connection.is_connected():
        connection.rollback()

except FileNotFoundError:
    print("\nError: Cleaned CSV file not found.")
    print("Expected path: data/cleaned_sales_data.csv")

except Exception as e:
    print("\nUnexpected Error:", e)
    if connection and connection.is_connected():
        connection.rollback()

finally:
    if cursor is not None:
        cursor.close()

    if connection is not None and connection.is_connected():
        connection.close()
        print("\nMySQL connection closed.")
