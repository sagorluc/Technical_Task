import logging
import time
from celery import shared_task
from orders.models import RepairOrder

logger = logging.getLogger(__name__)

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3})
def send_invoice(self, order_id):
    pass

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3})
def start_processing(self, order_id):
    order = RepairOrder.objects.get(id=order_id)
    order.status = "processing"
    order.save()
    logger.info("Order %s is now processing.", order.order_id)
    time.sleep(30)  # watching some processing time
    
    order.status = "completed"
    order.save()
    logger.info("Order %s is now completed.", order.order_id)
    
    return True