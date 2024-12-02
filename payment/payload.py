from . import constants as const 
from . import models


def get_payload(purchase: models.Purchase) -> dict:
    payload = {
        "isSandbox" : False,
        "storeID" : const.store_id,
        "successUrl" : const.return_url+purchase.tracker.key,
        "failUrl" : const.return_url+purchase.tracker.key,
        "cancelUrl" : const.return_url+purchase.tracker.key,
        "transactionID" : purchase.transaction_id,
        "transactionAmount" : purchase.payable_amount,
        "signature" : const.signature_key,
        "customerName" : purchase.user.get_full_name(),
        "customerEmail" : purchase.user.email,
        "customerMobile" : purchase.user.phone.number if hasattr(purchase.user, 'phone') else '018768815107'
    }

    return payload