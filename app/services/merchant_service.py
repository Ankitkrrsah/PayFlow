import secrets
from app.repositories import merchant_repo
from app.core.security import get_password_hash

def create_merchant(user_id: str, business_name: str) -> dict:
    """
    Creates a merchant and generates API keys.
    """
    # Generate API key (Using secrets that helps to generate random number)
    api_key_str = secrets.token_hex(32)
    api_key = f"mk_live_{api_key_str}"
    
    # Generate API secret
    api_secret_str = secrets.token_hex(32)
    api_secret = f"sk_live_{api_secret_str}"
    
    # Hash secret
    api_secret_hash = get_password_hash(api_secret)
    
    merchant = merchant_repo.create_merchant(
        user_id=user_id,
        business_name=business_name,
        api_key=api_key,
        api_secret_hash=api_secret_hash
    )
    
    #Returning the api secret only once 
    merchant["api_secret"] = api_secret
    return merchant
