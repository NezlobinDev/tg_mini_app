import asyncio
import time
from datetime import datetime, timedelta
from tasks import task_upd_file_data, task_check_new_files
import schedule
from app.settings.db import TORTOISE_ORM, MODELS
from tortoise import Tortoise


async def task_manager():
    """ Подзадачи """
    await Tortoise.init(
        config=TORTOISE_ORM,
        modules={model.split('.')[0]: model for model in MODELS},
    )
    await Tortoise.generate_schemas()

    schedule.every(60*5).seconds.do(task_check_new_files)
    schedule.every(5).seconds.do(task_upd_file_data)

    while True:
        all_jobs = schedule.get_jobs()
        runnable_jobs = (job for job in all_jobs if job.should_run)
        for job in runnable_jobs:
            function = job.job_func
            try:
                await function()
                job.last_run = datetime.now()
                job.next_run = datetime.now() + timedelta(seconds=job.interval)
            except Exception:
                pass
        time.sleep(1)

if __name__ == '__main__':
    asyncio.run(task_manager())
