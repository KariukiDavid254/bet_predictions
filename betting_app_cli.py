import argparse
import sqlite3

# Database connection.
conn = sqlite3.connect("betting_app.db")
cur = conn.cursor()

# Creating the desired tables.
cur.executescript('''
    -- table creations...

''')

# Commit the changes to the database.
conn.commit()

# Function to create a user
def create_user(username, email, password):
    cur.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username, email, password))
    conn.commit()
    print("User created successfully.")

# Function to create a bet
def create_bet(user_id, amount):
    cur.execute("INSERT INTO bets (user_id, amount, status) VALUES (?, ?, ?)",
                (user_id, amount, "Pending"))
    conn.commit()
    print("Bet placed successfully.")

# Function to get user balance
def get_user_balance(user_id):
    cur.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    balance = cur.fetchone()
    return balance[0] if balance else None

# Function to update user balance
def update_user_balance(user_id, amount):
    cur.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (amount, user_id))
    conn.commit()

# Function to update bet status
def update_bet_status(bet_id, status):
    cur.execute("UPDATE bets SET status = ? WHERE bet_id=?", (status, bet_id))
    conn.commit()

# Function to display table data
def display_table(table_name):
    cur.execute(f"SELECT * FROM {table_name}")
    data = cur.fetchall()
    print(f"\n{table_name.capitalize()} Table:")
    for row in data:
        print(row)

# Function to place a bet on a selection
def place_bet_on_selection(user_id, selection_id, amount):
    cur.execute("SELECT s.odds, u.balance FROM selections AS s "
                "INNER JOIN markets AS m ON s.market_id = m.market_id "
                "INNER JOIN users AS u ON u.user_id = ? "
                "WHERE s.selection_id = ? AND u.user_id = ?",
                (user_id, selection_id, user_id))
    result = cur.fetchone()

    if result is None:
        print("Invalid selection ID.")
        return

    odds, balance = result
    if balance < amount:
        print("Insufficient balance to place the bet.")
        return

    potential_winnings = amount * odds

    create_bet(user_id, amount)
    update_user_balance(user_id, -amount)

    print(f"Bet placed successfully! Potential winnings: {potential_winnings:.2f}")

# Function to calculate total winnings for a user
def calculate_total_winnings(user_id):
    cur.execute("SELECT SUM(amount * s.odds) FROM bets AS b "
                "INNER JOIN selections AS s ON b.bet_id = s.selection_id "
                "WHERE b.user_id = ? AND b.status = 'Won'", (user_id,))
    total_winnings = cur.fetchone()[0]
    if total_winnings is None:
        total_winnings = 0.0

    print(f"Total Winnings for User ID {user_id}: {total_winnings:.2f}")

# Function to view user's placed bets and their status
def view_user_bets(user_id):
    cur.execute("SELECT bet_id, amount, status FROM bets WHERE user_id = ?", (user_id,))
    bets = cur.fetchall()
    if not bets:
        print("No bets found for this user.")
    else:
        print(f"Placed bets for User ID {user_id}:")
        for bet in bets:
            bet_id, amount, status = bet
            print(f"Bet ID: {bet_id}, Amount: {amount:.2f}, Status: {status}")

# Function to display available selections for a market
def display_selections(market_id):
    cur.execute("SELECT selection_id, selection_name, odds FROM selections WHERE market_id = ?", (market_id,))
    selections = cur.fetchall()
    if not selections:
        print("No selections found for this market.")
    else:
        print(f"Available selections for Market ID {market_id}:")
        for selection in selections:
            selection_id, selection_name, odds = selection
            print(f"Selection ID: {selection_id}, Name: {selection_name}, Odds: {odds}")

# Function to simulate event outcomes and update bet statuses
def simulate_event_outcomes(event_id):
    cur.execute("SELECT s.selection_id, s.odds FROM selections AS s "
                "INNER JOIN markets AS m ON s.market_id = m.market_id "
                "INNER JOIN events AS e ON e.event_id = ? "
                "WHERE m.event_id = ?",
                (event_id, event_id))
    selections = cur.fetchall()

    if not selections:
        print("No selections found for this event.")
        return

    import random

    for selection in selections:
        selection_id, odds = selection
        outcome = random.choices(["Won", "Lost"], weights=[0.6, 0.4])[0]

        cur.execute("UPDATE bets SET status = ? WHERE bet_id IN "
                    "(SELECT bet_id FROM selections WHERE selection_id = ?)",
                    (outcome, selection_id))

        if outcome == "Won":
            cur.execute("SELECT user_id, amount FROM bets WHERE bet_id IN "
                        "(SELECT bet_id FROM selections WHERE selection_id = ?)",
                        (selection_id,))
            bets = cur.fetchall()

            for bet in bets:
                user_id, amount = bet
                winnings = amount * odds
                update_user_balance(user_id, winnings)

    conn.commit()
    print("Event outcomes simulated and bet statuses updated.")

# FUNCTIONALITIES

# Create users
users = [
    ("user1", "user1@gmail.com", "password1"),
    ("user2", "user2@gmail.com", "password2"),
    ("user3", "user3@gmail.com", "password3"),
    ("user4", "user4@gmail.com", "password4"),
    ("user5", "user5@gmail.com", "password5")
]
for user in users:
    username, email, password = user
    # Check if the user with the given email already exists
    cur.execute("SELECT user_id FROM users WHERE email = ?", (email,))
    existing_user = cur.fetchone()
    if existing_user:
        print(f"User with email '{email}' already exists. Skip creation.")
    else:
        create_user(username, email, password)

# Place bets on selections
place_bet_on_selection(1, 1, 10.00)
place_bet_on_selection(2, 2, 20.00)
place_bet_on_selection(3, 1, 30.00)
place_bet_on_selection(4, 2, 40.00)
place_bet_on_selection(5, 1, 50.00)

# View user bets
view_user_bets(1)
view_user_bets(2)
view_user_bets(3)
view_user_bets(4)
view_user_bets(5)

# Calculate total winnings for users
calculate_total_winnings(1)
calculate_total_winnings(2)
calculate_total_winnings(3)
calculate_total_winnings(4)
calculate_total_winnings(5)

# Display available selections for a market
display_selections(1)
display_selections(2)

# Simulate event outcomes and update bet statuses
simulate_event_outcomes(1)

# Displaying the tables
display_table("users")
display_table("bets")
display_table("events")
display_table("markets")
display_table("selections")

# Closing the database connection.
conn.close()

print("Tables created successfully.")
