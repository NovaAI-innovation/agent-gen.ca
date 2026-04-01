from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession

import eth_account

from ..core.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

from ..crud.user import get_user_by_wallet, create_update_user

from ..schemas.user import Token

from ..db.database import get_db


router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/siwe/verify", response_model=Token)
async def siwe_verify(message: str, signature: str, db: AsyncSession = Depends(get_db)):
    try:
        wallet_address = eth_account.Account.recover_message(
            eth_account.messages.encode_defunct(text=message)
        ).lower()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid SIWE signature")
    
    user = await create_update_user(db, wallet_address)
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
