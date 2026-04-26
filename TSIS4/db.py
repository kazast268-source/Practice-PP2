import psycopg2
from datetime import datetime

# --- НАСТРОЙКИ ПОДКЛЮЧЕНИЯ ---
# Обязательно впиши свои данные (user и password), которые ты задал в PostgreSQL
DB_CONFIG = {
    "dbname": "postgres",     
    "user": "aktannurdaulet",       
    "password": "123456789", 
    "host": "localhost",
    "port": "5432"
}

def get_connection():
    """Создает соединение с базой данных."""
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    """Создает таблицы players и game_sessions, если они еще не созданы."""
    conn = get_connection()
    cur = conn.cursor()
    
    # Таблица игроков (username уникален)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL
        );
    """)
    
    # Таблица игровых сессий (связана с игроком через player_id)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS game_sessions (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES players(id) ON DELETE CASCADE,
            score INTEGER NOT NULL,
            level_reached INTEGER NOT NULL,
            played_at TIMESTAMP DEFAULT NOW()
        );
    """)
    
    conn.commit()
    cur.close()
    conn.close()

def get_or_create_player(username):
    """
    Проверяет, есть ли игрок в базе. 
    Если нет — создает. Возвращает ID игрока.
    """
    conn = get_connection()
    cur = conn.cursor()
    
    # Пытаемся вставить игрока, если имя занято — просто ничего не делаем (ON CONFLICT)
    cur.execute("""
        INSERT INTO players (username) VALUES (%s)
        ON CONFLICT (username) DO NOTHING;
    """, (username,))
    
    # Получаем ID игрока (существующего или только что созданного)
    cur.execute("SELECT id FROM players WHERE username = %s;", (username,))
    player_id = cur.fetchone()[0]
    
    conn.commit()
    cur.close()
    conn.close()
    return player_id

def save_result(player_id, score, level):
    """Сохраняет результат игры в базу данных."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO game_sessions (player_id, score, level_reached)
        VALUES (%s, %s, %s);
    """, (player_id, score, level))
    conn.commit()
    cur.close()
    conn.close()

def get_personal_best(player_id):
    """Возвращает максимальный рекорд конкретного игрока."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT MAX(score) FROM game_sessions WHERE player_id = %s;", (player_id,))
    result = cur.fetchone()[0]
    cur.close()
    conn.close()
    return result if result is not None else 0
def get_top_scores(limit=10):
    """Получает топ-10 лучших результатов без вылетов."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT p.username, s.score, s.level_reached, s.played_at
            FROM game_sessions s
            JOIN players p ON s.player_id = p.id
            ORDER BY s.score DESC
            LIMIT %s;
        """, (limit,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows # Возвращает список кортежей
    except Exception as e:
        print(f"Ошибка БД в Leaderboard: {e}")
        return []