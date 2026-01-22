"""Authentication module for Streamlit app.

Handles Supabase authentication integration.
"""

import streamlit as st
from typing import Optional

from content_assistant.db.supabase_client import get_client


def check_authentication() -> bool:
    """Check if user is authenticated.

    Returns:
        True if user is authenticated, False otherwise
    """
    return st.session_state.get("authenticated", False)


def get_current_user() -> Optional[dict]:
    """Get current authenticated user info.

    Returns:
        User info dict or None if not authenticated
    """
    return st.session_state.get("user", None)


def show_login_form() -> bool:
    """Display login form and handle authentication.

    Returns:
        True if login successful, False otherwise
    """
    st.markdown("## Welcome to TheLifeCo Content Assistant")
    st.markdown("Please log in to continue.")

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log In")

        if submitted:
            if not email or not password:
                st.error("Please enter both email and password.")
                return False

            try:
                client = get_client()
                response = client.auth.sign_in_with_password({
                    "email": email,
                    "password": password,
                })

                if response.user:
                    st.session_state["authenticated"] = True
                    st.session_state["user"] = {
                        "id": response.user.id,
                        "email": response.user.email,
                    }
                    st.session_state["access_token"] = response.session.access_token
                    st.success("Login successful!")
                    st.rerun()
                    return True

            except Exception as e:
                st.error(f"Login failed: {str(e)}")
                return False

    # Show signup option
    st.markdown("---")
    st.markdown("Don't have an account?")

    with st.expander("Create Account"):
        with st.form("signup_form"):
            new_email = st.text_input("Email", key="signup_email")
            new_password = st.text_input("Password", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password")
            signup_submitted = st.form_submit_button("Sign Up")

            if signup_submitted:
                if not new_email or not new_password:
                    st.error("Please fill in all fields.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    try:
                        client = get_client()
                        response = client.auth.sign_up({
                            "email": new_email,
                            "password": new_password,
                        })

                        if response.user:
                            st.success("Account created! You can now log in.")
                            st.rerun()
                        else:
                            st.error("Signup failed. Please try again.")

                    except Exception as e:
                        st.error(f"Signup failed: {str(e)}")

    return False


def logout() -> None:
    """Log out the current user."""
    try:
        client = get_client()
        client.auth.sign_out()
    except Exception:
        pass  # Ignore errors during logout

    # Clear session state
    st.session_state["authenticated"] = False
    st.session_state["user"] = None
    st.session_state["access_token"] = None

    st.rerun()


def require_auth() -> bool:
    """Decorator-like function to require authentication.

    Use at the start of pages that require auth.

    Returns:
        True if authenticated, shows login form and returns False otherwise
    """
    if not check_authentication():
        show_login_form()
        return False
    return True
