"""Authentication module for Streamlit app.

Handles Supabase authentication integration including:
- Email/password login
- Google OAuth
- Password reset
"""

import streamlit as st
from typing import Optional

from content_assistant.db.supabase_client import get_client


def check_authentication() -> bool:
    """Check if user is authenticated.

    Returns:
        True if user is authenticated, False otherwise
    """
    # Check for OAuth callback
    _handle_oauth_callback()

    return st.session_state.get("authenticated", False)


def get_current_user() -> Optional[dict]:
    """Get current authenticated user info.

    Returns:
        User info dict or None if not authenticated
    """
    return st.session_state.get("user", None)


def _handle_oauth_callback():
    """Handle OAuth callback from Google sign-in."""
    # Check if we have OAuth tokens in URL params
    query_params = st.query_params

    if "access_token" in query_params:
        try:
            access_token = query_params.get("access_token")
            refresh_token = query_params.get("refresh_token", "")

            client = get_client()

            # Set the session with the tokens
            response = client.auth.set_session(access_token, refresh_token)

            if response.user:
                st.session_state["authenticated"] = True
                st.session_state["user"] = {
                    "id": response.user.id,
                    "email": response.user.email,
                }
                st.session_state["access_token"] = access_token

                # Clear URL params
                st.query_params.clear()
                st.rerun()

        except Exception:
            pass  # OAuth callback failed, show login form


def _get_redirect_url() -> str:
    """Get the redirect URL for OAuth."""
    # Try to get the current URL for Streamlit Cloud
    try:
        # For Streamlit Cloud, construct from secrets or use default
        import streamlit as st
        if hasattr(st, "secrets") and "REDIRECT_URL" in st.secrets:
            return st.secrets["REDIRECT_URL"]
    except Exception:
        pass

    # Default for local development
    return "http://localhost:8501"


def show_login_form() -> bool:
    """Display login form and handle authentication.

    Returns:
        True if login successful, False otherwise
    """
    st.markdown("## Welcome to TheLifeCo Content Assistant")
    st.markdown("*Self-improving AI content assistant for wellness marketing*")

    # Google Sign-In Button
    st.markdown("### Sign in with Google")
    if st.button("Continue with Google", type="primary", use_container_width=True):
        _sign_in_with_google()

    st.markdown("---")
    st.markdown("### Or use email")

    # Email/Password Login
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        col1, col2 = st.columns([1, 1])
        with col1:
            submitted = st.form_submit_button("Log In", use_container_width=True)
        with col2:
            forgot = st.form_submit_button("Forgot Password?", use_container_width=True)

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

        if forgot:
            if not email:
                st.error("Please enter your email address first.")
            else:
                _send_password_reset(email)

    # Show signup option
    st.markdown("---")
    st.markdown("Don't have an account?")

    with st.expander("Create Account"):
        with st.form("signup_form"):
            new_email = st.text_input("Email", key="signup_email")
            new_password = st.text_input("Password", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password")
            signup_submitted = st.form_submit_button("Sign Up", use_container_width=True)

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


def _sign_in_with_google():
    """Initiate Google OAuth sign-in."""
    try:
        client = get_client()
        redirect_url = _get_redirect_url()

        # Get the OAuth URL from Supabase
        response = client.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                "redirect_to": redirect_url,
            }
        })

        if response.url:
            # Redirect to Google OAuth
            st.markdown(f'<meta http-equiv="refresh" content="0;url={response.url}">', unsafe_allow_html=True)
            st.info("Redirecting to Google...")
        else:
            st.error("Failed to initiate Google sign-in. Please try again.")

    except Exception as e:
        st.error(f"Google sign-in failed: {str(e)}")
        st.info("Make sure Google OAuth is enabled in your Supabase dashboard.")


def _send_password_reset(email: str):
    """Send password reset email.

    Args:
        email: User's email address
    """
    try:
        client = get_client()
        redirect_url = _get_redirect_url()

        client.auth.reset_password_for_email(
            email,
            options={
                "redirect_to": f"{redirect_url}?reset=true",
            }
        )

        st.success(f"Password reset email sent to {email}. Check your inbox!")

    except Exception as e:
        st.error(f"Failed to send reset email: {str(e)}")


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
