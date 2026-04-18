"""
Background tasks with real weather API integration.
"""

import logging
import os
import requests
from app.celery_config import celery_app
from app.database import SessionLocal
from app.models import Task

logger = logging.getLogger(__name__)

# Get API key from environment
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


@celery_app.task(bind=True)
def process_task(self, task_id: str):
    """
    Background task to process a task with real weather API integration.
    
    Task format: "Get weather for [CITY_NAME]"
    Example: "Get weather for London"
    """
    
    db = SessionLocal()
    try:
        # ========== STEP 1: Get task from database ==========
        logger.info(f"[{task_id}] Worker: Starting task processing")
        task = db.query(Task).filter(Task.id == task_id).first()
        
        if not task:
            logger.error(f"[{task_id}] Worker: Task not found!")
            return {"error": f"Task {task_id} not found"}
        
        # ========== STEP 2: Update status to "in_progress" ==========
        task.status = "in_progress"
        db.commit()
        logger.info(f"[{task_id}] Worker: Status updated to 'in_progress'")
        
        # ========== STEP 3: Parse task description ==========
        description = task.description.strip()
        logger.info(f"[{task_id}] Worker: Task description: {description}")
        
        # Extract city name from description
        # Expected format: "Get weather for [CITY]"
        if description.lower().startswith("get weather for "):
            city = description.replace("Get weather for ", "").replace("get weather for ", "").strip()
        else:
            city = description  # Use whole description as city name
        
        logger.info(f"[{task_id}] Worker: Fetching weather for city: {city}")
        
        # ========== STEP 4: Call OpenWeather API ==========
        try:
            params = {
                "q": city,
                "appid": OPENWEATHER_API_KEY,
                "units": "metric"  # Use Celsius
            }
            
            logger.info(f"[{task_id}] Worker: Making API request to OpenWeatherMap...")
            response = requests.get(OPENWEATHER_URL, params=params, timeout=10)
            
            # Check if API call was successful
            if response.status_code != 200:
                error_msg = f"Weather API error: {response.status_code} - {response.text}"
                logger.error(f"[{task_id}] Worker: {error_msg}")
                
                task.status = "failed"
                task.result = error_msg
                db.commit()
                
                return {
                    "task_id": task_id,
                    "status": "failed",
                    "error": error_msg
                }
            
            # Parse API response
            data = response.json()
            
            # Extract relevant weather info
            weather_info = {
                "city": data.get("name"),
                "country": data.get("sys", {}).get("country"),
                "temperature": data.get("main", {}).get("temp"),
                "feels_like": data.get("main", {}).get("feels_like"),
                "humidity": data.get("main", {}).get("humidity"),
                "pressure": data.get("main", {}).get("pressure"),
                "description": data.get("weather", [{}])[0].get("description"),
                "wind_speed": data.get("wind", {}).get("speed"),
            }
            
            logger.info(f"[{task_id}] Worker: Successfully fetched weather data")
            logger.info(f"[{task_id}] Worker: Weather info: {weather_info}")
            
            # ========== STEP 5: Format result ==========
            result_message = (
                f"Weather in {weather_info['city']}, {weather_info['country']}: "
                f"{weather_info['temperature']}°C, "
                f"{weather_info['description'].capitalize()}, "
                f"Humidity: {weather_info['humidity']}%, "
                f"Wind: {weather_info['wind_speed']} m/s"
            )
            
            # ========== STEP 6: Update database with result ==========
            task.result = result_message
            task.status = "completed"
            db.commit()
            
            logger.info(f"[{task_id}] Worker: Task completed successfully")
            logger.info(f"[{task_id}] Worker: Result: {result_message}")
            
            return {
                "task_id": task_id,
                "status": "completed",
                "result": result_message,
                "weather_data": weather_info
            }
        
        except requests.exceptions.Timeout:
            error_msg = "Weather API request timed out (10 seconds)"
            logger.error(f"[{task_id}] Worker: {error_msg}")
            
            task.status = "failed"
            task.result = error_msg
            db.commit()
            
            return {
                "task_id": task_id,
                "status": "failed",
                "error": error_msg
            }
        
        except requests.exceptions.RequestException as e:
            error_msg = f"Weather API request failed: {str(e)}"
            logger.error(f"[{task_id}] Worker: {error_msg}")
            
            task.status = "failed"
            task.result = error_msg
            db.commit()
            
            return {
                "task_id": task_id,
                "status": "failed",
                "error": error_msg
            }
        
        except Exception as e:
            error_msg = f"Error processing weather data: {str(e)}"
            logger.error(f"[{task_id}] Worker: {error_msg}")
            
            task.status = "failed"
            task.result = error_msg
            db.commit()
            
            return {
                "task_id": task_id,
                "status": "failed",
                "error": error_msg
            }
    
    except Exception as e:
        # Catch any unexpected errors
        logger.error(f"[{task_id}] Worker: Unexpected error: {str(e)}", exc_info=True)
        
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if task:
                task.status = "failed"
                task.result = f"Error: {str(e)}"
                db.commit()
        except:
            logger.error(f"[{task_id}] Worker: Failed to update task status in database")
        
        return {
            "task_id": task_id,
            "status": "failed",
            "error": str(e)
        }
    
    finally:
        # Always close the database connection
        db.close()
        logger.info(f"[{task_id}] Worker: Database connection closed")