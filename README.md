# GenCare Backend Setup Guide

## Prerequisites
1. **XAMPP Installed**: Ensure MySQL is running via XAMPP Control Panel.
2. **Python Installed**: Ensure you have Python 3.x installed.

## Step 1: Database Setup
1. Open **phpMyAdmin** (usually at `http://localhost/phpmyadmin`).
2. Click on the **Import** tab.
3. Choose the `gencare_db.sql` file located in this directory (`/Applications/XAMPP/xamppfiles/htdocs/GenCare/gencare_db.sql`).
4. Click **Go** to create the database and tables.

## Step 2: Backend Setup
1. Open your terminal.
2. Navigate to this directory:
   ```bash
   cd /Applications/XAMPP/xamppfiles/htdocs/GenCare
   ```
3. Install the required Python packages:
   ```bash
   pip3 install -r requirements.txt
   ```
   *(Note: If you have permission issues, try `pip3` or use `sudo`, or create a virtual environment)*

## Step 3: Running the Server
1. Start the Flask server:
   ```bash
   python3 app.py
   ```
2. The server will start running at `http://0.0.0.0:5000`.

## Step 4: Connecting the iOS App
1. Find your Mac's local IP address (System Settings > Wi-Fi > Details... or run `ipconfig getifaddr en0` in terminal).
2. Update your iOS app's `NetworkManager` or `APIEndpoint` to point to `http://<YOUR_MAC_IP>:5000`.
   - Example: `http://192.168.1.5:5000`

## API Endpoints
- **POST /register**: JSON `{ "full_name": "...", "email": "...", "password": "...", "phone": "..." }`
- **POST /login**: JSON `{ "email": "...", "password": "..." }`
- **GET /profile/<user_id>**: Returns user details.
- **PUT /profile/<user_id>**: Update user details.
- **GET /lifestyle/<user_id>**: Returns lifestyle info.
- **PUT /lifestyle/<user_id>**: Update lifestyle info.
- **GET /family_health/<user_id>**: Returns family conditions.
- **POST /family_health/<user_id>**: Update all family conditions.
