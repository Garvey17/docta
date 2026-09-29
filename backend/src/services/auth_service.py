"""Authentication and User Service using Supabase Auth."""

import logging
from typing import Optional, Dict, Any
import jwt

from ..config import get_settings
from ..supabase_client import get_supabase_client
from ..schemas.auth import UserResponse, Token

logger = logging.getLogger(__name__)
settings = get_settings()


class AuthService:
    """Manages authentication with Supabase Auth."""

    @staticmethod
    async def sign_up(email: str, password: str, name: Optional[str] = None) -> Token:
        """Register a new user in Supabase Auth and create a profile."""
        supabase = get_supabase_client()
        user_name = name or email.split("@")[0]

        try:
            res = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {"data": {"name": user_name, "full_name": user_name}},
            })
        except Exception as e:
            logger.warning("Supabase sign_up error: %s", e)
            raise ValueError(str(e))

        user_id = str(res.user.id)
        access_token = getattr(res.session, "access_token", f"sb_token_{user_id}")
        refresh_token = getattr(res.session, "refresh_token", None)

        # Upsert profile in user_profiles
        try:
            profile_data = {
                "id": user_id,
                "email": email,
                "name": user_name,
                "daily_calorie_target": 2200,
                "daily_protein_target_g": 110.0,
                "daily_carbs_target_g": 250.0,
                "daily_fat_target_g": 65.0,
                "daily_fiber_target_g": 30.0,
                "daily_sodium_target_mg": 2300.0,
                "is_active": True,
                "is_admin": False,
            }
            supabase.from_("user_profiles").insert(profile_data).execute()
        except Exception as e:
            logger.debug("Could not insert user_profile: %s", e)

        user_resp = UserResponse(
            id=user_id,
            email=email,
            name=user_name,
            full_name=user_name,
            is_active=True,
            is_admin=False,
            dailyCalorieTarget=2200,
            dailyProteinTargetG=110.0,
            dailyCarbsTargetG=250.0,
            dailyFatTargetG=65.0,
            dailyFiberTargetG=30.0,
            dailySodiumTargetMg=2300.0,
        )

        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            refresh_token=refresh_token,
            user=user_resp,
        )

    @staticmethod
    async def login(email: str, password: str) -> Token:
        """Authenticate user against Supabase Auth."""
        supabase = get_supabase_client()
        try:
            res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        except Exception as e:
            logger.warning("Supabase sign_in error: %s", e)
            raise ValueError("Invalid email or password")

        user_id = str(res.user.id)
        access_token = getattr(res.session, "access_token", f"sb_token_{user_id}")
        refresh_token = getattr(res.session, "refresh_token", None)

        # Fetch profile
        user_name = email.split("@")[0]
        cal_target = 2200
        pro_target = 110.0
        carb_target = 250.0
        fat_target = 65.0
        fib_target = 30.0
        sod_target = 2300.0
        is_admin = False

        try:
            prof_res = supabase.from_("user_profiles").select("*").eq("id", user_id).execute()
            if prof_res.data:
                p = prof_res.data[0] if isinstance(prof_res.data, list) else prof_res.data
                user_name = p.get("name") or p.get("full_name") or user_name
                cal_target = p.get("daily_calorie_target") or cal_target
                pro_target = float(p.get("daily_protein_target_g") or pro_target)
                carb_target = float(p.get("daily_carbs_target_g") or carb_target)
                fat_target = float(p.get("daily_fat_target_g") or fat_target)
                fib_target = float(p.get("daily_fiber_target_g") or fib_target)
                sod_target = float(p.get("daily_sodium_target_mg") or sod_target)
                is_admin = bool(p.get("is_admin", False))
        except Exception as e:
            logger.debug("Failed reading user profile: %s", e)

        user_resp = UserResponse(
            id=user_id,
            email=email,
            name=user_name,
            full_name=user_name,
            is_active=True,
            is_admin=is_admin,
            dailyCalorieTarget=cal_target,
            dailyProteinTargetG=pro_target,
            dailyCarbsTargetG=carb_target,
            dailyFatTargetG=fat_target,
            dailyFiberTargetG=fib_target,
            dailySodiumTargetMg=sod_target,
        )

        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            refresh_token=refresh_token,
            user=user_resp,
        )

    @staticmethod
    async def get_user_from_token(token: str) -> Optional[UserResponse]:
        """Validate bearer token and retrieve user profile."""
        supabase = get_supabase_client()
        try:
            user_res = supabase.auth.get_user(token)
            if user_res and getattr(user_res, "user", None):
                u = user_res.user
                u_id = str(getattr(u, "id", ""))
                u_email = str(getattr(u, "email", ""))
                u_meta = getattr(u, "user_metadata", {}) or {}
                u_name = u_meta.get("name") or u_meta.get("full_name") or getattr(u, "name", None) or u_email.split("@")[0]

                # Check user_profiles table for nutrition targets
                cal_target = 2200
                pro_target = 110.0
                carb_target = 250.0
                fat_target = 65.0
                fib_target = 30.0
                sod_target = 2300.0
                is_admin = False

                try:
                    p_res = supabase.from_("user_profiles").select("*").eq("id", u_id).execute()
                    if p_res.data:
                        p = p_res.data[0] if isinstance(p_res.data, list) else p_res.data
                        u_name = p.get("name") or p.get("full_name") or u_name
                        cal_target = p.get("daily_calorie_target") or cal_target
                        pro_target = float(p.get("daily_protein_target_g") or pro_target)
                        carb_target = float(p.get("daily_carbs_target_g") or carb_target)
                        fat_target = float(p.get("daily_fat_target_g") or fat_target)
                        fib_target = float(p.get("daily_fiber_target_g") or fib_target)
                        sod_target = float(p.get("daily_sodium_target_mg") or sod_target)
                        is_admin = bool(p.get("is_admin", False))
                except Exception:
                    pass

                return UserResponse(
                    id=u_id,
                    email=u_email,
                    name=u_name,
                    full_name=u_name,
                    is_active=True,
                    is_admin=is_admin,
                    dailyCalorieTarget=cal_target,
                    dailyProteinTargetG=pro_target,
                    dailyCarbsTargetG=carb_target,
                    dailyFatTargetG=fat_target,
                    dailyFiberTargetG=fib_target,
                    dailySodiumTargetMg=sod_target,
                )
        except Exception as e:
            logger.debug("Supabase auth.get_user error: %s", e)

        # Fallback decode if signed with local JWT secret
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            sub = payload.get("sub")
            email = payload.get("email", "user@docta.ng")
            is_admin = payload.get("is_admin", False)
            if sub:
                return UserResponse(
                    id=str(sub),
                    email=email,
                    name=email.split("@")[0],
                    full_name=email.split("@")[0],
                    is_active=True,
                    is_admin=is_admin,
                )
        except Exception:
            pass

        return None

    @staticmethod
    async def logout(token: Optional[str] = None) -> bool:
        """Sign out user from Supabase Auth."""
        supabase = get_supabase_client()
        try:
            if hasattr(supabase, "auth") and hasattr(supabase.auth, "sign_out"):
                try:
                    supabase.auth.sign_out(token)
                except TypeError:
                    supabase.auth.sign_out()
            return True
        except Exception as e:
            logger.warning("Sign out error: %s", e)
            return True
