import json
import os
from datetime import datetime, timedelta
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout

# File to store streak & coins
STREAK_FILE = "rewards.json"

# Load or initialize streak data
def load_streak_data():
    if os.path.exists(STREAK_FILE):
        with open(STREAK_FILE, "r") as file:
            return json.load(file)
    else:
        return {"last_login": None, "streak": 0, "coins": 0}

# Save streak data
def save_streak_data(data):
    with open(STREAK_FILE, "w") as file:
        json.dump(data, file)

# Update streak on user login
def update_streak():
    data = load_streak_data()
    today = datetime.today().date()

    # If first login ever
    if data["last_login"] is None:
        data["streak"] = 1
        data["coins"] = 10  # Give initial coins
    else:
        last_login = datetime.strptime(data["last_login"], "%Y-%m-%d").date()

        # If user logs in on the next day, increase streak
        if last_login == today - timedelta(days=1):
            data["streak"] += 1
        # If user missed a day, reset streak
        elif last_login < today - timedelta(days=1):
            data["streak"] = 1

        # Award coins dynamically
        data["coins"] += data["streak"] * 5  # More coins for higher streaks

    # Save today's login date
    data["last_login"] = str(today)
    save_streak_data(data)

    return data

# Spend coins on premium features
def spend_coins(amount):
    data = load_streak_data()
    if data["coins"] >= amount:
        data["coins"] -= amount
        save_streak_data(data)
        return True  # Successfully spent coins
    return False  # Not enough coins

class StreakApp(App):
    def build(self):
        """Loads the UI from streak.kv"""
        self.root = Builder.load_file("streak.kv")
        self.update_ui()
        return self.root

    def update_ui(self):
        """Updates the UI with the latest streak and coin count."""
        data = update_streak()
        self.root.ids.streak_label.text = f"Streak: {data['streak']} days"
        self.root.ids.coins_label.text = f"Coins: {data['coins']}"

    def remove_ads(self):
        """Spend 50 coins to remove ads for 1 day."""
        if spend_coins(50):
            self.root.ids.coins_label.text = f"Coins: {load_streak_data()['coins']}"
            print("✅ Ads removed for 1 day!")
        else:
            print("❌ Not enough coins!")

    def unlock_premium(self):
        """Spend 100 coins for a premium feature."""
        if spend_coins(100):
            self.root.ids.coins_label.text = f"Coins: {load_streak_data()['coins']}"
            print("✅ Premium feature unlocked!")
        else:
            print("❌ Not enough coins!")

if __name__ == "__main__":
    StreakApp().run()
