"""Authentication module for Streamlit app.

Handles Supabase authentication integration including:
- Email/password login
- Google OAuth
- Password reset
"""

import streamlit as st
from typing import Optional

from content_assistant.db.supabase_client import get_client
from content_assistant.ui.styles import inject_custom_css, get_logo_base64, get_logo_path


def check_authentication() -> bool:
    """Check if user is authenticated.

    Returns:
        True if user is authenticated, False otherwise
    """
    # Check for OAuth callback
    _handle_oauth_callback()

    # Check for password reset callback
    if _is_password_reset_callback():
        return False  # Show reset form instead of main app

    return st.session_state.get("authenticated", False)


def _is_password_reset_callback() -> bool:
    """Check if this is a password reset callback."""
    query_params = st.query_params
    return "reset" in query_params or "type" in query_params and query_params.get("type") == "recovery"


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
    # Inject custom CSS
    inject_custom_css()

    # Check if this is a password reset callback
    if _is_password_reset_callback():
        return _show_reset_password_form()

    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Logo and title
        logo_path = get_logo_path()
        if logo_path.exists():
            col_logo1, col_logo2, col_logo3 = st.columns([1, 2, 1])
            with col_logo2:
                st.image(str(logo_path), use_container_width=True)

        st.markdown("""
            <div style="text-align: center; margin: 1.5rem 0 2rem 0;">
                <h1 style="font-size: 1.5rem; font-weight: 600; color: #1A1A1A; margin-bottom: 0.5rem;">
                    Welcome Back
                </h1>
                <p style="color: #6B7280; font-size: 0.875rem;">
                    Sign in to your content assistant
                </p>
            </div>
        """, unsafe_allow_html=True)

        # Google Sign-In Button
        if st.button("Continue with Google", type="secondary", use_container_width=True):
            _sign_in_with_google()

        # Divider
        st.markdown("""
            <div style="display: flex; align-items: center; margin: 1.5rem 0;">
                <div style="flex: 1; height: 1px; background: #E5E7EB;"></div>
                <span style="padding: 0 1rem; color: #9CA3AF; font-size: 0.75rem;">or continue with email</span>
                <div style="flex: 1; height: 1px; background: #E5E7EB;"></div>
            </div>
        """, unsafe_allow_html=True)

        # Email/Password Login
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", placeholder="Enter your password")

            submitted = st.form_submit_button("Sign In", type="primary", use_container_width=True)

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
                        st.rerun()
                        return True

                except Exception as e:
                    st.error(f"Invalid email or password")
                    return False

        # Forgot password link
        if st.button("Forgot your password?", type="tertiary" if hasattr(st, "button") else "secondary"):
            st.session_state["show_forgot_password"] = True
            st.rerun()

        # Show forgot password form
        if st.session_state.get("show_forgot_password"):
            st.markdown("---")
            st.markdown("**Reset Password**")
            reset_email = st.text_input("Enter your email", key="reset_email", placeholder="you@example.com")
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("Send Reset Link", use_container_width=True):
                    if reset_email:
                        _send_password_reset(reset_email)
                    else:
                        st.error("Please enter your email.")
            with col_b:
                if st.button("Cancel", use_container_width=True):
                    st.session_state["show_forgot_password"] = False
                    st.rerun()

        # Divider
        st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)

        # Sign up section
        st.markdown("""
            <p style="text-align: center; color: #6B7280; font-size: 0.875rem;">
                Don't have an account?
            </p>
        """, unsafe_allow_html=True)

        if st.button("Create Account", use_container_width=True):
            st.session_state["show_signup"] = True
            st.rerun()

        # Show signup form
        if st.session_state.get("show_signup"):
            st.markdown("---")
            with st.form("signup_form"):
                st.markdown("**Create Your Account**")
                new_email = st.text_input("Email", key="signup_email", placeholder="you@example.com")
                new_password = st.text_input("Password", type="password", key="signup_password", placeholder="Min. 6 characters")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")

                col_a, col_b = st.columns(2)
                with col_a:
                    signup_submitted = st.form_submit_button("Sign Up", type="primary", use_container_width=True)
                with col_b:
                    cancel = st.form_submit_button("Cancel", use_container_width=True)

                if cancel:
                    st.session_state["show_signup"] = False
                    st.rerun()

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
                                st.success("Account created! Check your email to verify.")
                                st.session_state["show_signup"] = False
                            else:
                                st.error("Signup failed. Please try again.")

                        except Exception as e:
                            st.error(f"Signup failed: {str(e)}")

    return False


def _show_reset_password_form() -> bool:
    """Display password reset form.

    Returns:
        True if password reset successful, False otherwise
    """
    # Inject custom CSS
    inject_custom_css()

    # Center the form
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Logo
        logo_path = get_logo_path()
        if logo_path.exists():
            col_logo1, col_logo2, col_logo3 = st.columns([1, 2, 1])
            with col_logo2:
                st.image(str(logo_path), use_container_width=True)

        st.markdown("""
            <div style="text-align: center; margin: 1.5rem 0 2rem 0;">
                <h1 style="font-size: 1.5rem; font-weight: 600; color: #1A1A1A; margin-bottom: 0.5rem;">
                    Reset Your Password
                </h1>
                <p style="color: #6B7280; font-size: 0.875rem;">
                    Enter your new password below
                </p>
            </div>
        """, unsafe_allow_html=True)

        with st.form("reset_password_form"):
            new_password = st.text_input("New Password", type="password", placeholder="Min. 6 characters")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")

        submitted = st.form_submit_button("Update Password", type="primary", use_container_width=True)

        if submitted:
            if not new_password or not confirm_password:
                st.error("Please fill in both password fields.")
                return False

            if new_password != confirm_password:
                st.error("Passwords do not match.")
                return False

            if len(new_password) < 6:
                st.error("Password must be at least 6 characters.")
                return False

            try:
                client = get_client()

                # Get access token from URL (Supabase sends it in the hash/query)
                query_params = st.query_params
                access_token = query_params.get("access_token")

                if access_token:
                    # Set the session first
                    refresh_token = query_params.get("refresh_token", "")
                    client.auth.set_session(access_token, refresh_token)

                # Update the password
                client.auth.update_user({"password": new_password})

                st.success("Password updated successfully! You can now log in with your new password.")

                # Clear URL params
                st.query_params.clear()

                # Show link to login
                if st.button("Go to Login"):
                    st.rerun()

                return True

            except Exception as e:
                st.error(f"Failed to update password: {str(e)}")
                return False

        st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)
        if st.button("Back to Login", use_container_width=True):
            st.query_params.clear()
            st.rerun()

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
