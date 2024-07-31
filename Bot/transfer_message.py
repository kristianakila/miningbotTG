from .connect_wallet import send_transaction
import time
from base64 import urlsafe_b64encode
from .cfg import WITHDRAW_ADDRESS
from pytoniq_core import begin_cell


def get_comment_message(destination_address: str, amount: int, comment: str) -> dict:

    data = {
        "address": destination_address,
        "amount": str(amount),
        "payload": urlsafe_b64encode(
            begin_cell()
            .store_uint(0, 32)  # op code for comment message
            .store_string(comment)  # store comment
            .end_cell()  # end cell
            .to_boc()  # convert it to boc
        ).decode(),  # encode it to urlsafe base64
    }

    return data


async def send_transaction_tonconnect(user_id: int):
    transaction = {
        "valid_until": int(time.time() + 3600),
        "messages": [
            get_comment_message(
                destination_address=WITHDRAW_ADDRESS,
                amount=100000000,
                comment="💸 Вывод $BULL (@BullMining_Bot)",
            )
        ],
    }

    try:
        result = await send_transaction(
            transaction=transaction,
            chat_id=user_id,
        )

        return result
    except Exception as e:
        print(e)
        return False
