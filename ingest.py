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
    ('ORD-1003', 'Mechanical Keyboard', 89.99, 'Premier'),
    ('ORD-1004', 'Gaming Headset', 79.99, 'Standard'),
    ('ORD-1005', 'USB-C Charger', 19.99, 'Premier'),
    ('ORD-1006', '4K Monitor', 399.99, 'Standard'),
    ('ORD-1007', 'Laptop Cooling Pad', 45.50, 'Premier'),
    ('ORD-1008', 'External SSD 1TB', 150.00, 'Standard'),
    ('ORD-1009', 'Smartphone Stand', 12.99, 'Standard'),
    ('ORD-1010', 'Bluetooth Speaker', 59.99, 'Premier'),
    ('ORD-1011', 'Portable Hard Drive 2TB', 110.00, 'Standard'),
    ('ORD-1012', 'Gaming Mouse Pro', 65.99, 'Premier'),
    ('ORD-1013', 'HD Webcam', 49.99, 'Standard'),
    ('ORD-1014', 'USB Hub 7-Port', 29.99, 'Premier'),
    ('ORD-1015', 'Laptop Backpack', 70.00, 'Standard'),
    ('ORD-1016', 'Mechanical Keyboard RGB', 129.99, 'Premier'),
    ('ORD-1017', 'Noise Cancelling Headphones', 249.99, 'Premier'),
    ('ORD-1018', 'Tablet Stand Adjustable', 22.50, 'Standard'),
    ('ORD-1019', 'Wireless Charging Pad', 34.99, 'Premier'),
    ('ORD-1020', 'Ergonomic Office Mouse', 39.99, 'Standard')
]

cursor.executemany('INSERT INTO orders VALUES (?,?,?,?)', sample_orders)
conn.commit()
conn.close()
print("orders.db created successfully in /data folder.")