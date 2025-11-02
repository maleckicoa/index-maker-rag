#!/usr/bin/env python3
"""
Scheduled runner for make_index_tool.
"""
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from .index_maker import make_index_tool

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def main():
    """Main scheduler setup."""
    scheduler = BlockingScheduler()
    
    scheduler.add_job(
        make_index_tool,
        IntervalTrigger(hours=36),  # Run every 20 seconds 
        id='make_index_job',
        name='Make Index Process',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Scheduler started. Running make_index_tool every 36 hours")


if __name__ == "__main__":
    main()

