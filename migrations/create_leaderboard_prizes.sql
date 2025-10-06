-- Таблица для хранения призов за рейтинг
CREATE TABLE IF NOT EXISTS leaderboard_prizes (
    id SERIAL PRIMARY KEY,
    period_type VARCHAR(20) NOT NULL, -- 'daily', 'weekly', 'monthly'
    period_start TIMESTAMP NOT NULL,
    period_end TIMESTAMP NOT NULL,
    place INTEGER NOT NULL, -- 1, 2, 3
    user_id INTEGER REFERENCES users(id),
    prize_amount DECIMAL(10, 5) NOT NULL,
    awarded_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'awarded', 'failed'
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(period_type, period_start, place)
);

-- Индексы для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_leaderboard_prizes_period ON leaderboard_prizes(period_type, period_start);
CREATE INDEX IF NOT EXISTS idx_leaderboard_prizes_user ON leaderboard_prizes(user_id);
CREATE INDEX IF NOT EXISTS idx_leaderboard_prizes_status ON leaderboard_prizes(status);

-- Комментарии
COMMENT ON TABLE leaderboard_prizes IS 'Призы за места в рейтинге';
COMMENT ON COLUMN leaderboard_prizes.period_type IS 'Тип периода: daily, weekly, monthly';
COMMENT ON COLUMN leaderboard_prizes.place IS 'Место в рейтинге: 1, 2, 3';
COMMENT ON COLUMN leaderboard_prizes.status IS 'Статус выплаты: pending, awarded, failed';
