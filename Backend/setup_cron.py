#!/usr/bin/env python
import os
import sys
from crontab import CronTab

def setup_cron_job():
    """Set up a cron job to run the cleanup_reservations.py script every 5 minutes"""
    try:
        # Get the current user
        current_user = os.getenv('USER')
        
        # Create a new cron tab for the current user
        cron = CronTab(user=current_user)
        
        # Get the absolute path to the script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        cleanup_script = os.path.join(script_dir, 'cleanup_reservations.py')
        
        # Get the Python interpreter path
        python_path = sys.executable
        
        # Create the command
        command = f"{python_path} {cleanup_script} >> {script_dir}/cron_cleanup.log 2>&1"
        
        # Check if the job already exists
        for job in cron:
            if cleanup_script in str(job):
                print(f"Cron job for {cleanup_script} already exists. Removing it.")
                cron.remove(job)
        
        # Create a new job that runs every 5 minutes
        job = cron.new(command=command)
        job.minute.every(5)
        
        # Write the crontab
        cron.write()
        
        print(f"Cron job set up successfully to run every 5 minutes:")
        print(f"Command: {command}")
        
        return True
    
    except Exception as e:
        print(f"Error setting up cron job: {str(e)}")
        return False

if __name__ == "__main__":
    setup_cron_job()
