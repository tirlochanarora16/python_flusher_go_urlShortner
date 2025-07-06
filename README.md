# Redis Flusher

A lightweight Python utility that flushes URL hit counts from Redis to PostgreSQL. This is a critical component of a URL shortener system that batches access count updates for better performance.

## Overview

This project serves as a **cron job utility** for a URL shortener application. Instead of updating the database on every URL visit (which would be expensive), the main application stores hit counts in Redis and this utility periodically flushes them to PostgreSQL using efficient bulk operations.

## How It Works

1. **URL Visits**: When users visit shortened URLs, the main Go application increments counters in Redis (keys like `url_hits:abc123`)
2. **Batch Processing**: This utility runs periodically (via cron) to collect all Redis hit counts
3. **Bulk Update**: Performs a single SQL bulk update to add the hit counts to the database
4. **Cleanup**: Removes the processed keys from Redis

## Architecture

```
User visits short URL → Go app increments Redis counter → Cron job runs → Bulk update to PostgreSQL
```

## Features

- ✅ **Efficient bulk operations** - Updates multiple URLs in a single SQL query
- ✅ **Atomic operations** - Uses database transactions for data consistency
- ✅ **Redis cleanup** - Automatically removes processed keys
- ✅ **Error handling** - Graceful handling of empty Redis states
- ✅ **Environment-based configuration** - Secure credential management

## Prerequisites

- Python 3.8+
- Redis server
- PostgreSQL database
- Virtual environment (recommended)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd redis_flusher
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your actual credentials
   ```

## Configuration

Create a `.env` file with the following variables:

```env
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# PostgreSQL Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
```

## Database Schema

Ensure your PostgreSQL database has a `urls` table with the following structure:

```sql
CREATE TABLE urls (
    id SERIAL PRIMARY KEY,
    short_code VARCHAR(255) UNIQUE NOT NULL,
    original_url TEXT NOT NULL,
    access_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Usage

### Manual Execution

Run the flusher manually:

```bash
python main.py
```

### Cron Job Setup

Add to your crontab to run every 5 minutes:

```bash
# Edit crontab
crontab -e

# Add this line (adjust path as needed)
*/5 * * * * cd /path/to/redis_flusher && /path/to/venv/bin/python main.py
```

### Docker (Optional)

If you prefer Docker, create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

## How the Bulk Update Works

The utility uses PostgreSQL's efficient bulk update syntax:

```sql
UPDATE urls
SET access_count = access_count + data.count
FROM (VALUES %s) AS data(short_code, count)
WHERE urls.short_code = data.short_code;
```

This single query updates multiple URLs at once, making it much faster than individual updates.

## Monitoring

The utility provides basic logging:

- `"No keys to flush!"` - When Redis is empty
- `"Flushed X keys."` - Success message with count
- Returns status object for programmatic monitoring

## Integration with Go URL Shortener

In your Go application, when a user visits a short URL:

```go
// Increment hit count in Redis
redisClient.Incr(ctx, "url_hits:" + shortCode)
```

The Redis flusher will later collect these counters and update the database.

## Performance Benefits

- **Reduced database load**: Instead of N database writes, you get 1 bulk update
- **Better user experience**: No database latency on URL visits
- **Scalable**: Can handle thousands of URL visits efficiently
- **Cost-effective**: Reduces database connection overhead

## Troubleshooting

### Common Issues

1. **Connection errors**: Check your `.env` file and network connectivity
2. **Permission errors**: Ensure database user has UPDATE permissions
3. **Empty results**: Normal when no URLs have been visited recently

### Logs

Monitor the output for:
- Connection success/failure messages
- Number of keys processed
- Any error messages

## Security Considerations

- Keep `.env` file secure and never commit it to version control
- Use strong passwords for Redis and PostgreSQL
- Consider using connection pooling for production
- Implement proper error handling in production environments

## Development

For development and testing:

```bash
# Activate virtual environment
source venv/bin/activate

# Run with debug output
python main.py

# Test with sample data
# Add some test keys to Redis manually for testing
```

## License

[Your License Here]

## Contributing

[Your Contributing Guidelines Here] 