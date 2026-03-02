CREATE TABLE IF NOT EXISTS risk_history (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  overall_risk_percent INT NOT NULL,
  overall_risk_level VARCHAR(20) NOT NULL,
  dominant_category VARCHAR(50) NOT NULL,
  risk_breakdown JSON NOT NULL,
  response_json JSON NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
