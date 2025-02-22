class TestAuthAPI:
    def test_auth_token(self, super_admin_token):
        """
        Checks that the authorization token is retrieved correctly.
        """
        assert super_admin_token, "Authorization token should not be empty"
        assert super_admin_token.startswith("eyJ"), "Token should be a valid JWT"