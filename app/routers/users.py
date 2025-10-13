from fastapi import APIRouter, Depends, HTTPException, status,Response,Request
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from typing import List
import logging

from app.database import get_db
from app import models, schemas, auth
from app.email_service import email_service

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/register", response_model=schemas.UserResponse)
async def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    logger.info(f"Attempting to register user with email: {user.email} and username: {user.username}")
    try:
        # Check if user already exists
        existing_user = db.query(models.User).filter(
            (models.User.email == user.email) | (models.User.username == user.username)
        ).first()
        if existing_user:
            if existing_user.email == user.email:
                logger.warning(f"Registration failed: Email {user.email} already registered")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "error": "Email already registered",
                        "message": "An account with this email address already exists. Please use a different email or try logging in."
                    }
                )
            if existing_user.username == user.username:
                logger.warning(f"Registration failed: Username {user.username} already taken")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "error": "Username already taken",
                        "message": "This username is already in use. Please choose a different username."
                    }
                )
        
        # Validate email format
        if "@" not in user.email or "." not in user.email:
            logger.warning(f"Invalid email format: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": "Invalid email format",
                    "message": "Please provide a valid email address."
                }
            )
        
        # Validate username
        if len(user.username) < 3:
            logger.warning(f"Invalid username: {user.username} (too short)")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": "Invalid username",
                    "message": "Username must be at least 3 characters long."
                }
            )
        
        # Validate password strength
        if len(user.password) < 8:
            logger.warning(f"Password too weak for user: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": "Password too weak",
                    "message": "Password must be at least 8 characters long."
                }
            )
        
        # Create new user
        hashed_password = auth.get_password_hash(user.password)
        db_user = models.User(
            email=user.email,
            username=user.username,
            hashed_password=hashed_password,
            balance=0.0
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"User registered successfully: {user.email}")
        
        # Send welcome email (optional - can fail without breaking registration)
        try:
            await email_service.send_welcome_email(user.email, user.username)
            logger.info(f"Welcome email sent to: {user.email}")
        except Exception as e:
            logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")
        
        return db_user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed for {user.email}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Registration failed",
                "message": "An error occurred during registration. Please try again."
            }
        )
@router.post("/login", response_model=schemas.UnifiedLoginResponse)
async def login_user(login_data: schemas.UserLogin, db: Session = Depends(get_db), response: Response = None):
    """Unified login endpoint for both users and admins"""
    logger.info(f"Attempting unified login for: {login_data.email}")
    try:
        # Use the unified authentication function
        auth_result = auth.authenticate_user_or_admin(login_data.email, login_data.password, db)
        
        if not auth_result:
            logger.warning(f"Login failed: Invalid credentials for {login_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "Invalid credentials",
                    "message": "Email or password is incorrect."
                }
            )
        
        user_type = auth_result["type"]
        user_data = auth_result["data"]
        
        # Create access token
        access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth.create_access_token(
            data={"sub": user_data.email}, expires_delta=access_token_expires
        )
        
        # Create refresh token (only for regular users)
        refresh_token = None
        if user_type == "user":
            refresh_token_expires = timedelta(days=auth.REFRESH_TOKEN_EXPIRE_DAYS)
            refresh_token = auth.create_refresh_token(
                data={"sub": user_data.email}, expires_delta=refresh_token_expires
            )
            
            # Set refresh token as HttpOnly cookie for users
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=False,  # Set to True in production (HTTPS)
                samesite="lax",
                max_age=int(refresh_token_expires.total_seconds())
            )
        
        # Prepare user data based on type
        if user_type == "user":
            user_response_data = {
                "id": user_data.id,
                "email": user_data.email,
                "username": user_data.username,
                "balance": user_data.balance,
                "wallet_address": user_data.wallet_address,
                "status": user_data.status,
                "created_at": user_data.created_at,
                "updated_at": user_data.updated_at
            }
        else:  # admin
            user_response_data = {
                "id": user_data.id,
                "email": user_data.email,
                "role": user_data.role,
                "permissions": user_data.permissions,
                "is_active": user_data.is_active,
                "last_login": user_data.last_login,
                "created_at": user_data.created_at,
                "updated_at": user_data.updated_at
            }
            
            # Update admin last login
            user_data.last_login = datetime.utcnow()
            db.commit()
        
        logger.info(f"Unified login successful for {login_data.email} as {user_type}")
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_type": user_type,
            "user_data": user_response_data,
            "refresh_token": refresh_token
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unified login failed for {login_data.email}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Login failed",
                "message": "An error occurred during login. Please try again."
            }
        )

@router.post("/refresh", response_model=schemas.Token)
async def refresh_access_token(request: Request, response: Response, db: Session = Depends(get_db)):
    """Refresh access token using refresh token from HttpOnly cookie"""
    logger.info("Attempting to refresh access token")
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        logger.warning("Refresh failed: No refresh token provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "No refresh token",
                "message": "No refresh token provided."
            }
        )
    
    try:
        user = auth.verify_refresh_token(refresh_token, db)
        access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth.create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        # Create a new refresh token to rotate it
        refresh_token_expires = timedelta(days=auth.REFRESH_TOKEN_EXPIRE_DAYS)
        new_refresh_token = auth.create_refresh_token(
            data={"sub": user.email}, expires_delta=refresh_token_expires
        )
        # Update the refresh token cookie
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            secure=False,  # Set to True in production (HTTPS)
            samesite="lax",
            max_age=int(refresh_token_expires.total_seconds())
        )
        logger.info(f"Access token refreshed successfully for {user.email}")
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Refresh token failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "Invalid refresh token",
                "message": "The provided refresh token is invalid or expired."
            }
        )

@router.post("/logout")
async def logout(response: Response):
    """Log out user by clearing the refresh token cookie"""
    logger.info("Attempting to log out user")
    try:
        response.delete_cookie(
            key="refresh_token",
            httponly=True,
            secure=False,  # Set to True in production (HTTPS)
            samesite="lax"
        )
        logger.info("User logged out successfully")
        return {"message": "Logged out successfully"}
    except Exception as e:
        logger.error(f"Logout failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Logout failed",
                "message": "An error occurred during logout. Please try again."
            }
        )

@router.get("/me", response_model=schemas.UserResponse)
async def get_current_user_info(current_user: models.User = Depends(auth.get_current_active_user)):
    """Get current user information"""
    logger.info(f"Fetching user info for {current_user.email}")
    try:
        return current_user
    except Exception as e:
        logger.error(f"Failed to fetch user info for {current_user.email}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Failed to fetch user info",
                "message": "An error occurred while fetching user information."
            }
        )

@router.put("/me", response_model=schemas.UserResponse)
async def update_user_info(
    wallet_address: str,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update user wallet address"""
    logger.info(f"Updating wallet address for user {current_user.email}")
    try:
        current_user.wallet_address = wallet_address
        db.commit()
        db.refresh(current_user)
        logger.info(f"Wallet address updated successfully for {current_user.email}")
        return current_user
    except Exception as e:
        logger.error(f"Failed to update wallet address for {current_user.email}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Update failed",
                "message": "An error occurred while updating user information."
            }
        )

@router.get("/", response_model=List[schemas.UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""
    logger.info(f"Fetching all users (skip={skip}, limit={limit})")
    try:
        users = db.query(models.User).offset(skip).limit(limit).all()
        logger.info(f"Retrieved {len(users)} users")
        return users
    except Exception as e:
        logger.error(f"Failed to fetch users: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Failed to fetch users",
                "message": "An error occurred while fetching users."
            }
        )

@router.put("/deactivate", response_model=schemas.UserResponse)
async def deactivate_user(
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Deactivate current user account"""
    logger.info(f"Deactivating account for {current_user.email}")
    try:
        current_user.status = "inactive"
        db.commit()
        db.refresh(current_user)
        logger.info(f"Account deactivated successfully for {current_user.email}")
        return current_user
    except Exception as e:
        logger.error(f"Deactivation failed for {current_user.email}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Deactivation failed",
                "message": "An error occurred while deactivating your account."
            }
        )

@router.put("/reactivate", response_model=schemas.UserResponse)
async def reactivate_user(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Reactivate user account (only works if user is inactive)"""
    logger.info(f"Attempting to reactivate account for {current_user.email}")
    try:
        if current_user.status != "inactive":
            logger.warning(f"Reactivation failed: Account {current_user.email} is {current_user.status}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Invalid status",
                    "message": "Only inactive accounts can be reactivated."
                }
            )
        
        current_user.status = "active"
        db.commit()
        db.refresh(current_user)
        logger.info(f"Account reactivated successfully for {current_user.email}")
        return current_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reactivation failed for {current_user.email}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Reactivation failed",
                "message": "An error occurred while reactivating your account."
            }
        )

@router.delete("/me")
async def delete_current_user(
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete current user account (soft delete)"""
    logger.info(f"Deleting account for {current_user.email}")
    try:
        current_user.status = "deleted"
        db.commit()
        logger.info(f"Account deleted successfully for {current_user.email}")
        return {
            "message": "Account deleted successfully",
            "detail": "Your account has been deactivated. You can contact support to reactivate it."
        }
    except Exception as e:
        logger.error(f"Account deletion failed for {current_user.email}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Account deletion failed",
                "message": "An error occurred while deleting your account. Please try again."
            }
        )

@router.put("/admin/{user_id}/suspend", response_model=schemas.UserResponse)
async def suspend_user(
    user_id: int,
    reason: str = None,
    current_admin: models.Admin = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """Suspend a user account (admin only)"""
    logger.info(f"Admin {current_admin.email} attempting to suspend user ID {user_id}")
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            logger.warning(f"Suspension failed: User ID {user_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "User not found",
                    "message": "The specified user does not exist."
                }
            )
        
        if user.status == "suspended":
            logger.warning(f"Suspension failed: User {user.email} already suspended")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "User already suspended",
                    "message": "This user is already suspended."
                }
            )
        
        user.status = "suspended"
        db.commit()
        db.refresh(user)
        log_message = f"User {user.email} suspended by admin {current_admin.email}"
        if reason:
            log_message += f" - Reason: {reason}"
        logger.info(log_message)
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Suspension failed for user ID {user_id}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Suspension failed",
                "message": "An error occurred while suspending the user."
            }
        )

@router.put("/admin/{user_id}/unsuspend", response_model=schemas.UserResponse)
async def unsuspend_user(
    user_id: int,
    current_admin: models.Admin = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """Unsuspend a user account (admin only)"""
    logger.info(f"Admin {current_admin.email} attempting to unsuspend user ID {user_id}")
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            logger.warning(f"Unsuspension failed: User ID {user_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "User not found",
                    "message": "The specified user does not exist."
                }
            )
        
        if user.status != "suspended":
            logger.warning(f"Unsuspension failed: User {user.email} is not suspended")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "User not suspended",
                    "message": "This user is not currently suspended."
                }
            )
        
        user.status = "active"
        db.commit()
        db.refresh(user)
        logger.info(f"User {user.email} unsuspended by admin {current_admin.email}")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unsuspension failed for user ID {user_id}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Unsuspension failed",
                "message": "An error occurred while unsuspending the user."
            }
        )

@router.get("/admin/users", response_model=List[schemas.UserResponse])
async def get_users_by_status(
    status: str = None,
    skip: int = 0,
    limit: int = 100,
    current_admin: models.Admin = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """Get users filtered by status (admin only)"""
    logger.info(f"Admin {current_admin.email} fetching users with status {status} (skip={skip}, limit={limit})")
    try:
        query = db.query(models.User)
        
        if status:
            if status not in ["active", "inactive", "suspended", "deleted"]:
                logger.warning(f"Invalid status filter: {status}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "Invalid status",
                        "message": "Status must be 'active', 'inactive', 'suspended', or 'deleted'."
                    }
                )
            query = query.filter(models.User.status == status)
        
        users = query.offset(skip).limit(limit).all()
        logger.info(f"Retrieved {len(users)} users for admin {current_admin.email}")
        return users
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch users for admin {current_admin.email}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Failed to fetch users",
                "message": "An error occurred while fetching users."
            }
        )