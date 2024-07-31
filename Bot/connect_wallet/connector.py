import asyncio
from pytoniq_core import Address
from pytonconnect import TonConnect, exceptions
from .tc_storage import TcStorage
import logging

logging.basicConfig(level=logging.INFO, filename="log.log")


MANIFEST_URL = (
    "https://raw.githubusercontent.com/Muvan97/Bull/main/tonconnect-manifest.json"
)

wallets_list = TonConnect.get_wallets()


def get_connector(chat_id: int):
    return TonConnect(MANIFEST_URL, storage=TcStorage(chat_id))


async def connect_wallet(chat_id: int, wallet_name: str):
    connector = get_connector(chat_id)

    wallet = None

    for w in wallets_list:
        if w["name"] == wallet_name:
            wallet = w
            break

    if wallet is None:
        raise Exception(f"Unknown wallet: {wallet_name}")

    generated_url = await connector.connect(wallet)

    return generated_url, connector


async def wait_connection(connector: get_connector):
    for i in range(1, 60):
        await asyncio.sleep(1)
        if connector.connected:
            if connector.account.address:
                wallet_address = connector.account.address
                wallet_address = Address(wallet_address).to_str(is_bounceable=False)
                return wallet_address
            return False

    return f"Timeout error!"


async def disconnect_wallet(chat_id: int):
    try:
        connector = get_connector(chat_id)
        await connector.restore_connection()
        await connector.disconnect()
    except Exception as _ex:
        pass


async def send_transaction(transaction: dict, chat_id: int):
    try:
        connector = TonConnect(MANIFEST_URL, storage=TcStorage(chat_id))
        await connector.restore_connection()
        tx = await asyncio.wait_for(
            connector.send_transaction(transaction=transaction), 300
        )
        logging.warning(tx)
        return True
    except asyncio.TimeoutError:
        return False
    except exceptions.UserRejectsError:
        return False
    except Exception as e:
        logging.error(e)
        return False


async def get_app_name(chat_id: int):
    connector = get_connector(chat_id)
    await connector.restore_connection()
    try:
        return connector.wallet.device.app_name
    except Exception as e:
        print(e)
        return "Кошелёк"
