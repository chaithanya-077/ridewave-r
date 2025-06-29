import sqlite3

def view_database():
    # Connect to the database
    conn = sqlite3.connect('ridewave.db')
    cursor = conn.cursor()

    print("\n=== BIKES ===")
    cursor.execute("SELECT * FROM bike")
    bikes = cursor.fetchall()
    for bike in bikes:
        print(f"\nID: {bike[0]}")
        print(f"Name: {bike[1]}")
        print(f"Model: {bike[2]}")
        print(f"Category: {bike[3]}")
        print(f"Price: ₹{bike[4]}/day")
        print(f"Speed: {bike[5]}")
        print(f"Image: {bike[6]}")
        print(f"Description: {bike[7]}")

    print("\n=== USERS ===")
    cursor.execute("SELECT * FROM user")
    users = cursor.fetchall()
    for user in users:
        print(f"\nID: {user[0]}")
        print(f"Username: {user[1]}")
        print(f"Email: {user[2]}")
        print(f"Is Admin: {user[4]}")

    print("\n=== BOOKINGS ===")
    cursor.execute("SELECT * FROM booking")
    bookings = cursor.fetchall()
    for booking in bookings:
        print(f"\nID: {booking[0]}")
        print(f"User ID: {booking[1]}")
        print(f"Bike ID: {booking[2]}")
        print(f"Pickup Date: {booking[3]}")
        print(f"Return Date: {booking[4]}")
        print(f"Total Cost: ₹{booking[5]}")
        print(f"Status: {booking[6]}")
        print(f"Created At: {booking[7]}")

    # Close the connection
    conn.close()

if __name__ == '__main__':
    view_database() 