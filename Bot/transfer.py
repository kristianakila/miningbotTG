from pytonapi import AsyncTonapi
from pytonapi.exceptions import TONAPINotFoundError, TONAPIInternalServerError
from pytoniq import LiteBalancer, WalletV4R2, begin_cell
from .cfg import *


async def getaddrbydns(dns: str):
    tonapi = AsyncTonapi(TON_API_KEY)
    try:
        raw = (await tonapi.dns.resolve(dns)).wallet.address.to_raw()
        addr = await tonapi.accounts.parse_address(raw)
        return addr.non_bounceable.b64url
    except TONAPINotFoundError:
        return 404
    except TONAPIInternalServerError:
        return 400


async def TransferJetton(
    jetton_master_address: str, destination_wallet: str, amount: float
):
    provider = LiteBalancer.from_mainnet_config(2)
    await provider.start_up()

    wallet = await WalletV4R2.from_mnemonic(
        provider=provider, mnemonics=WITHDRAW_ADDRESS_MNEMONIC
    )
    USER_ADDRESS = wallet.address

    if destination_wallet.endswith(".ton") or destination_wallet.endswith(".t.me"):
        destination_wallet = await getaddrbydns(destination_wallet)

    USER_JETTON_WALLET = (
        await provider.run_get_method(
            address=jetton_master_address,
            method="get_wallet_address",
            stack=[begin_cell().store_address(USER_ADDRESS).end_cell().begin_parse()],
        )
    )[0].load_address()
    forward_payload = (
        begin_cell()
        .store_uint(0, 32)  # TextComment op-code
        .store_snake_string("💵 Выплата $BULL за майнинг")
        .end_cell()
    )
    transfer_cell = (
        begin_cell()
        .store_uint(0xF8A7EA5, 32)  # Jetton Transfer op-code
        .store_uint(0, 64)  # query_id
        .store_coins(int(amount * 1e9))  # Jetton amount to transfer in nanojetton
        .store_address(destination_wallet)  # Destination address
        .store_address(USER_ADDRESS)  # Response address
        .store_bit(0)  # Custom payload is None
        .store_coins(1)  # Ton forward amount in nanoton
        .store_bit(1)  # Store forward_payload as a reference
        .store_ref(forward_payload)  # Forward payload
        .end_cell()
    )

    if len(destination_wallet) == 48:
        try:
            await wallet.transfer(
                destination=USER_JETTON_WALLET,
                amount=int(0.05 * 1e9),
                body=transfer_cell,
            )
            return True
        except:
            transfer = {"destination": destination_wallet, "amount": int(0.086 * 1e9)}
            await wallet.transfer(**transfer)
            return False
        finally:
            await provider.close_all()


async def ReturnTon(destination_wallet: str):
    provider = LiteBalancer.from_mainnet_config(2)
    await provider.start_up()

    wallet = await WalletV4R2.from_mnemonic(
        provider=provider, mnemonics=WITHDRAW_ADDRESS_MNEMONIC
    )

    if destination_wallet.endswith(".ton") or destination_wallet.endswith(".t.me"):
        destination_wallet = await getaddrbydns(destination_wallet)

    if len(destination_wallet) == 48:
        try:
            transfer = {"destination": destination_wallet, "amount": int(0.086 * 1e9)}
            await wallet.transfer(**transfer)
            return True
        except:
            return False
        finally:
            await provider.close_all()
