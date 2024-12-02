import constants as const

def resolve_trx_check_url(trx: str):
    return f"https://secure.aamarpay.com/api/v1/trxcheck/request.php?request_id={trx}&store_id={const.store_id}&signature_key={const.signature_key}&type=json"

if __name__ == '__main__':
    import requests
    print(requests.get(resolve_trx_check_url('TYT21909724100305181962Q5')).json())