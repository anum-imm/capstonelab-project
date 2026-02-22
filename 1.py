import sqlite3

# Connect to the database file
conn = sqlite3.connect('data/orders.db')
cursor = conn.cursor()

# Create table
cursor.execute('''CREATE TABLE IF NOT EXISTS orders 
                  (id TEXT, item TEXT, price REAL, customer_tier TEXT)''')

# Insert mock data
sample_orders = [
    ('ORD-1001', 'Gaming Laptop', 1200.00, 'Premier'),
    ('ORD-1002', 'Wireless Mouse', 25.50, 'Standard'),
    ('ORD-1003', 'Mechanical Keyboard', 89.99, 'Premier')
]

cursor.executemany('INSERT INTO orders VALUES (?,?,?,?)', sample_orders)
conn.commit()
conn.close()
print("orders.db created successfully in /data folder.")