from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
from app.config import settings

security = HTTPBasic()


def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Verify admin credentials using HTTP Basic Auth
    Default: admin / admin (change in production)
    """
    correct_username = secrets.compare_digest(
        credentials.username.encode("utf-8"), 
        settings.admin_username.encode("utf-8")
    )
    correct_password = secrets.compare_digest(
        credentials.password.encode("utf-8"),
        settings.admin_password.encode("utf-8")
    )
    
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return credentials.username
