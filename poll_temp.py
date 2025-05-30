from app.scheduler import poll_temperature, start_scheduler
from app.database import init_db

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    
    print("Starting temperature polling scheduler...")
    scheduler = start_scheduler()
    
    try:
        # This will block until the scheduler is shut down
        scheduler._event.wait()
    except (KeyboardInterrupt, SystemExit):
        print("Shutting down scheduler...")
        scheduler.shutdown() 