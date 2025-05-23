"""
TEC Scheduler - Central automation coordinator for The Elidoras Codex.
This script manages scheduled tasks for content generation, news updates, and maintenance.

Usage:
    python -m scripts.tec_scheduler [--run-now TASK_NAME]
    
    Optional arguments:
        --run-now: Immediately run a specific task (news, crypto, clickup)
        --list-tasks: Show scheduled tasks and their next run times
        --create-windows-task: Create a Windows scheduled task to run on startup
"""
import os
import sys
import time
import argparse
import logging
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
import subprocess

# Add parent directory to the Python path for imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import required modules
from dotenv import load_dotenv

# Configure logging
logs_dir = os.path.join(project_root, "logs")
os.makedirs(logs_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(logs_dir, f"scheduler_{datetime.now().strftime('%Y%m%d')}.log"), 'a'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("TECScheduler")

# Load environment variables
load_dotenv(os.path.join(project_root, 'config', '.env'))

# Get automation settings
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "300"))  # Default: 5 minutes
DEBUG_MODE = os.getenv("DEBUG_MODE", "true").lower() == "true"

# News categories for rotation (in priority order)
NEWS_CATEGORIES = ["tech", "science", "digital_rights", "crypto", "sustainability", "business", "culture", "policy"]
# Lower priority categories that will be used less frequently
OCCASIONAL_CATEGORIES = ["gaming", "sports"]

def run_task(task_name, *args):
    """
    Run a specific task as a subprocess.
    
    Args:
        task_name: Name of the task to run
        args: Additional command line arguments
    """
    logger.info(f"Running task: {task_name}")
    
    try:
        task_map = {
            "news": ["python", "-m", "scripts.daily_news_automation"],
            "crypto": ["python", "-m", "scripts.crypto_news_automation"],
            "clickup": ["python", "-m", "agents.airth_agent", "--clickup"]
        }
        
        if task_name not in task_map:
            logger.error(f"Unknown task: {task_name}")
            return
        
        # Build the command
        command = task_map[task_name]
        if args:
            command.extend(args)
        
        # Log the command being executed
        logger.info(f"Executing command: {' '.join(command)}")
        
        # Run the process and capture output
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Get output
        stdout, stderr = process.communicate()
        
        # Log the output
        if stdout:
            logger.info(f"Task output: {stdout}")
        
        if stderr:
            logger.error(f"Task error output: {stderr}")
        
        if process.returncode == 0:
            logger.info(f"Task {task_name} completed successfully")
            return True, stdout
        else:
            logger.error(f"Task {task_name} failed with return code {process.returncode}")
            return False, stderr
    
    except Exception as e:
        logger.error(f"Error running task {task_name}: {e}")
        return False, str(e)

def get_daily_news_category():
    """
    Get a category for the daily news using a weighted selection based on the day of the week.
    More important categories have higher chances of being selected.
    
    Returns:
        Selected category name
    """
    today = datetime.now()
    day_of_week = today.weekday()  # 0=Monday, 6=Sunday
    
    # Use different category selection strategies based on the day of the week
    if day_of_week < 5:  # Weekday: focus on main tech topics
        # 80% chance to select from main categories, 20% chance for occasional categories
        if random.random() < 0.8:
            # Weight selection based on position in the list (first items have higher weight)
            weights = [max(5, 10 - i) for i in range(len(NEWS_CATEGORIES))]
            return random.choices(NEWS_CATEGORIES, weights=weights, k=1)[0]
        else:
            return random.choice(OCCASIONAL_CATEGORIES)
    else:  # Weekend: more variety
        # 60% chance to select from main categories, 40% chance for occasional categories
        if random.random() < 0.6:
            return random.choice(NEWS_CATEGORIES)
        else:
            return random.choice(OCCASIONAL_CATEGORIES)

def schedule_daily_news():
    """Run the daily news automation task."""
    logger.info("Running scheduled daily news task")
    
    # Randomly select a geo-region for variety (improves SEO by targeting different regions)
    geo_regions = ["US", "UK", "CA", "AU", "IN", "DE", "FR"]
    # Higher weight for US region (50% chance)
    weights = [5, 2, 2, 2, 1, 1, 1]
    selected_region = random.choices(geo_regions, weights=weights, k=1)[0]
    
    # Get a category based on the day
    selected_category = get_daily_news_category()
    
    logger.info(f"Selected region {selected_region} and category {selected_category} for today's news")
    
    # Run the daily news automation with both geo-targeting and category
    success, output = run_task("news", "--geo", selected_region, "--category", selected_category)
    
    # If first attempt fails, try with a different category
    if not success:
        logger.warning(f"First news attempt with category {selected_category} failed, trying with tech category")
        return run_task("news", "--geo", selected_region, "--category", "tech")
    
    return success, output

def schedule_crypto_news():
    """Run the crypto news automation task."""
    logger.info("Running scheduled crypto news task")
    
    # Rotate focus coins for variety (improves SEO by covering different cryptocurrencies)
    coin_groups = [
        "BTC,ETH,SOL",
        "BTC,ADA,DOT",
        "ETH,XRP,AVAX",
        "BTC,MATIC,LINK"
    ]
    selected_coins = random.choice(coin_groups)
    
    return run_task("crypto", "--coins", selected_coins)

def schedule_clickup_tasks():
    """Process ready tasks from ClickUp."""
    logger.info("Running scheduled ClickUp task processing")
    return run_task("clickup")

def init_scheduler():
    """Initialize the task scheduler with predefined schedules."""
    logger.info("Initializing the TEC scheduler")
    
    # Schedule daily news at 8 AM
    schedule.every().day.at("08:00").do(schedule_daily_news)
    logger.info("Scheduled daily news for 08:00 every day")
    
    # Schedule crypto updates at 16:30 (market close summary)
    schedule.every().day.at("16:30").do(schedule_crypto_news)
    logger.info("Scheduled crypto updates for 16:30 every day")
    
    # Schedule ClickUp task processing 3 times per day
    schedule.every().day.at("09:30").do(schedule_clickup_tasks)
    schedule.every().day.at("13:30").do(schedule_clickup_tasks)
    schedule.every().day.at("17:30").do(schedule_clickup_tasks)
    logger.info("Scheduled ClickUp task processing for 09:30, 13:30, and 17:30 every day")
    
    # Add more scheduled tasks as needed
    
    # If in debug mode, add more frequent test tasks
    if DEBUG_MODE:
        logger.info("Debug mode enabled - adding test tasks")
        # Add a heartbeat log message every 30 minutes
        schedule.every(30).minutes.do(lambda: logger.info("Debug heartbeat - scheduler is running"))

def run_scheduler():
    """Run the scheduler main loop."""
    logger.info("TEC Scheduler started")
    
    init_scheduler()
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Scheduler error: {e}")
        
    logger.info("TEC Scheduler stopped")

def create_windows_scheduled_task():
    """
    Create a Windows scheduled task to run this scheduler on system startup.
    This requires administrator privileges.
    """
    try:
        script_path = os.path.abspath(__file__)
        python_path = sys.executable
        
        # Build the XML for the task
        xml_content = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}</Date>
    <Author>TEC Admin</Author>
    <Description>TEC Content Automation Scheduler</Description>
    <URI>\\TEC\\ContentScheduler</URI>
  </RegistrationInfo>
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
    </LogonTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <DisallowStartOnRemoteAppSession>false</DisallowStartOnRemoteAppSession>
    <UseUnifiedSchedulingEngine>true</UseUnifiedSchedulingEngine>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{python_path}</Command>
      <Arguments>-m scripts.tec_scheduler</Arguments>
      <WorkingDirectory>{os.path.dirname(script_path)}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
"""
        
        # Write the XML to a temporary file
        xml_path = os.path.join(project_root, "temp_task.xml")
        with open(xml_path, "w") as f:
            f.write(xml_content)
        
        # Create the task using schtasks command
        subprocess.run(["schtasks", "/Create", "/TN", "TEC\\ContentScheduler", "/XML", xml_path, "/F"], check=True)
        
        # Remove the temporary XML file
        os.remove(xml_path)
        
        logger.info("Created Windows scheduled task 'TEC\\ContentScheduler' successfully")
    except Exception as e:
        logger.error(f"Error creating Windows scheduled task: {e}")

def show_scheduled_tasks():
    """Display currently scheduled tasks."""
    logger.info("Currently scheduled tasks:")
    
    for job in schedule.get_jobs():
        next_run = job.next_run
        time_until = (next_run - datetime.now()) if next_run else timedelta(0)
        
        job_info = f"- {job.job_func.__name__}: "
        job_info += f"Next run at {next_run.strftime('%Y-%m-%d %H:%M:%S')} "
        job_info += f"({str(time_until).split('.')[0]} from now)"
        
        logger.info(job_info)
        print(job_info)

if __name__ == "__main__":
    logger.info("TEC Scheduler script started")
    
    parser = argparse.ArgumentParser(description="TEC Content Automation Scheduler")
    parser.add_argument("--run-now", type=str, help="Run a specific task immediately (news, crypto, clickup)")
    parser.add_argument("--create-windows-task", action="store_true", help="Create a Windows scheduled task for this scheduler")
    parser.add_argument("--list-tasks", action="store_true", help="Show scheduled tasks")
    parser.add_argument("--category", type=str, help="Specify a category for the news task (only used with --run-now news)")
    
    args = parser.parse_args()
    
    if args.run_now:
        if args.run_now == "news" and args.category:
            run_task(args.run_now, "--category", args.category)
        else:
            run_task(args.run_now)
    elif args.create_windows_task:
        create_windows_scheduled_task()
    elif args.list_tasks:
        init_scheduler()
        show_scheduled_tasks()
    else:
        # Run the scheduler main loop
        run_scheduler()