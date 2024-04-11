'''
This is the entry point of the Trendit³ Flask application.

It creates an instance of the application and runs it.

@author Emmanuel Olowu
@link: https://github.com/zeddyemy
@package Trendit³
'''
from app import create_app, celery_app
from app.jobs import update_pending_tasks

app = create_app()

'''
@celery_app.schedule
def periodic_tasks():
    # Schedule the update_pending_tasks task to run every minute
    update_pending_tasks.s().schedule(run_at="interval", every='60 seconds')

if __name__ == '__main__':
    app.run(debug=True)

    # Start the Celery worker in the background
    celery_app.worker_main()
'''