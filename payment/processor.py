from .payload import get_payload
from . import models



class PaymentProcessor:

    def __init__(self, purchase: models.Purchase) -> None:
        self.purchase = purchase

    def request_gateway(self):
        if not self.purchase.is_closed:
            self.purchase.update_transaction_id()
            payload = get_payload(self.invoice)
            from aamarpay.aamarpay import aamarPay
            _ = aamarPay(**payload)
            return _.payment()
        
        return None
