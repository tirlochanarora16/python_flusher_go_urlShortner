import os
import psycopg2
import psycopg2.extras
import redis

from dotenv import load_dotenv
load_dotenv()

def lambda_handler():
    r = redis.Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), password=os.getenv("REDIS_PASSWORD"), db=0)

    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

    cur = conn.cursor()

    # get all keys for url_hits
    keys: list[bytes] = r.keys("url_hits:*")

    if len(keys) == 0:
        print("No keys to flush!")
        return

    data = []
    for key in keys:
        short_code = (key.decode('utf-8')).split(":")[1]
        short_code_value = int((r.get(key)).decode('utf-8'))
        data.append((short_code, short_code_value))
    
    sql = """
        UPDATE urls
        SET access_count = access_count + data.count
        FROM (VALUES %s) AS data(short_code, count)
        WHERE urls.short_code = data.short_code;
    """
    
    psycopg2.extras.execute_values(cur, sql, data)
    conn.commit()

    r.delete(*keys)

    print(f"Flushed {len(keys)} keys.")
    return {"status": f"Flushed {len(keys)} keys"}


if __name__ == "__main__":
    lambda_handler()