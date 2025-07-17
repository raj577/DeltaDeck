import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import os

from angel_api import AngelOneClient, AuthenticationManager, AngelOneError

class TestAngelOneError:
    """Test cases for AngelOneError exception"""
    
    def test_error_with_known_code(self):
        error = AngelOneError("AG8001")
        assert error.error_code == "AG8001"
        assert error.message == "Invalid Token"
        assert str(error) == "AG8001: Invalid Token"
    
    def test_error_with_unknown_code(self):
        error = AngelOneError("UNKNOWN")
        assert error.error_code == "UNKNOWN"
        assert error.message == "Unknown error"
    
    def test_error_with_custom_message(self):
        error = AngelOneError("AG8001", "Custom message")
        assert error.message == "Custom message"

class TestAuthenticationManager:
    """Test cases for AuthenticationManager"""
    
    @pytest.fixture
    def auth_manager(self):
        with patch('angel_api.SmartConnect') as mock_smart_connect:
            return AuthenticationManager(
                api_key="test_key",
                client_code="test_client",
                password="test_password",
                totp_token="test_token"
            )
    
    @pytest.mark.asyncio
    async def test_successful_authentication(self, auth_manager):
        # Mock successful authentication response
        mock_response = {
            'status': True,
            'data': {
                'jwtToken': 'test_jwt_token',
                'refreshToken': 'test_refresh_token'
            }
        }
        
        with patch('pyotp.TOTP') as mock_totp:
            mock_totp.return_value.now.return_value = "123456"
            auth_manager.smart_api.generateSession.return_value = mock_response
            auth_manager.smart_api.getfeedToken.return_value = "test_feed_token"
            
            result = await auth_manager.authenticate()
            
            assert result['status'] == 'success'
            assert result['auth_token'] == 'test_jwt_token'
            assert result['refresh_token'] == 'test_refresh_token'
            assert result['feed_token'] == 'test_feed_token'
            assert auth_manager.auth_token == 'test_jwt_token'
    
    @pytest.mark.asyncio
    async def test_failed_authentication(self, auth_manager):
        # Mock failed authentication response
        mock_response = {
            'status': False,
            'errorcode': 'AB1000',
            'message': 'Invalid credentials'
        }
        
        with patch('pyotp.TOTP') as mock_totp:
            mock_totp.return_value.now.return_value = "123456"
            auth_manager.smart_api.generateSession.return_value = mock_response
            
            with pytest.raises(AngelOneError) as exc_info:
                await auth_manager.authenticate()
            
            assert exc_info.value.error_code == 'AB1000'
    
    def test_session_validity_check(self, auth_manager):
        # Test valid session
        auth_manager.auth_token = "test_token"
        auth_manager.session_expiry = datetime.now() + timedelta(hours=1)
        assert auth_manager.is_session_valid() == True
        
        # Test expired session
        auth_manager.session_expiry = datetime.now() - timedelta(hours=1)
        assert auth_manager.is_session_valid() == False
        
        # Test session expiring soon (within 5 minutes)
        auth_manager.session_expiry = datetime.now() + timedelta(minutes=3)
        assert auth_manager.is_session_valid() == False

class TestAngelOneClient:
    """Test cases for AngelOneClient"""
    
    @pytest.fixture
    def mock_env_vars(self):
        env_vars = {
            'ANGEL_API_KEY': 'test_api_key',
            'ANGEL_CLIENT_CODE': 'test_client_code',
            'ANGEL_PASSWORD': 'test_password',
            'ANGEL_TOTP_TOKEN': 'test_totp_token'
        }
        
        with patch.dict(os.environ, env_vars):
            yield env_vars
    
    def test_client_initialization_success(self, mock_env_vars):
        with patch('angel_api.AuthenticationManager'):
            client = AngelOneClient()
            assert client.api_key == 'test_api_key'
            assert client.client_code == 'test_client_code'
    
    def test_client_initialization_missing_credentials(self):
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                AngelOneClient()
            
            assert "Missing required Angel One API credentials" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_authenticate_method(self, mock_env_vars):
        with patch('angel_api.AuthenticationManager') as mock_auth_manager:
            mock_auth_instance = Mock()
            mock_auth_manager.return_value = mock_auth_instance
            
            # Mock async method
            async def mock_authenticate():
                return {'status': 'success'}
            mock_auth_instance.authenticate = mock_authenticate
            
            client = AngelOneClient()
            result = await client.authenticate()
            
            assert result['status'] == 'success'
    
    @pytest.mark.asyncio
    async def test_ensure_authenticated(self, mock_env_vars):
        with patch('angel_api.AuthenticationManager') as mock_auth_manager:
            mock_auth_instance = Mock()
            mock_auth_manager.return_value = mock_auth_instance
            
            # Mock async method
            async def mock_ensure_valid_session():
                return True
            mock_auth_instance.ensure_valid_session = mock_ensure_valid_session
            
            client = AngelOneClient()
            result = await client.ensure_authenticated()
            
            assert result == True
    
    @pytest.mark.asyncio
    async def test_get_option_greeks_success(self, mock_env_vars):
        with patch('angel_api.AuthenticationManager') as mock_auth_manager:
            mock_auth_instance = Mock()
            mock_auth_manager.return_value = mock_auth_instance
            
            # Mock async method
            async def mock_ensure_valid_session():
                return True
            mock_auth_instance.ensure_valid_session = mock_ensure_valid_session
            
            # Mock SmartConnect instance
            mock_smart_api = Mock()
            mock_auth_instance.smart_api = mock_smart_api
            
            # Mock successful option Greeks response
            mock_response = {
                'status': True,
                'data': [
                    {
                        'name': 'NIFTY',
                        'expiry': '25JAN2024',
                        'strikePrice': '21000.000000',
                        'optionType': 'CE',
                        'delta': '0.492400',
                        'gamma': '0.002800',
                        'theta': '-4.091800',
                        'vega': '2.296700',
                        'impliedVolatility': '16.330000'
                    }
                ]
            }
            mock_smart_api.optionGreek.return_value = mock_response
            
            client = AngelOneClient()
            result = await client.get_option_greeks('NIFTY', '25JAN2024')
            
            assert len(result) == 1
            assert result[0]['name'] == 'NIFTY'
            assert result[0]['delta'] == '0.492400'
            mock_smart_api.optionGreek.assert_called_once_with({
                'name': 'NIFTY',
                'expirydate': '25JAN2024'
            })
    
    @pytest.mark.asyncio
    async def test_get_option_greeks_failure(self, mock_env_vars):
        with patch('angel_api.AuthenticationManager') as mock_auth_manager:
            mock_auth_instance = Mock()
            mock_auth_manager.return_value = mock_auth_instance
            
            # Mock async method
            async def mock_ensure_valid_session():
                return True
            mock_auth_instance.ensure_valid_session = mock_ensure_valid_session
            
            # Mock SmartConnect instance
            mock_smart_api = Mock()
            mock_auth_instance.smart_api = mock_smart_api
            
            # Mock failed response
            mock_response = {
                'status': False,
                'errorcode': 'AB1009',
                'message': 'Symbol Not Found'
            }
            mock_smart_api.optionGreek.return_value = mock_response
            
            client = AngelOneClient()
            
            with pytest.raises(AngelOneError) as exc_info:
                await client.get_option_greeks('INVALID', '25JAN2024')
            
            assert exc_info.value.error_code == 'AB1009'
    
    @pytest.mark.asyncio
    async def test_setup_websocket_success(self, mock_env_vars):
        with patch('angel_api.AuthenticationManager') as mock_auth_manager:
            with patch('angel_api.SmartWebSocketV2') as mock_websocket:
                mock_auth_instance = Mock()
                mock_auth_manager.return_value = mock_auth_instance
                
                # Mock async method
                async def mock_ensure_valid_session():
                    return True
                mock_auth_instance.ensure_valid_session = mock_ensure_valid_session
                mock_auth_instance.auth_token = 'test_auth_token'
                mock_auth_instance.feed_token = 'test_feed_token'
                
                mock_ws_instance = Mock()
                mock_websocket.return_value = mock_ws_instance
                
                client = AngelOneClient()
                
                def dummy_callback(data):
                    pass
                
                result = await client.setup_websocket(dummy_callback)
                
                assert result == mock_ws_instance
                mock_websocket.assert_called_once_with(
                    'test_auth_token',
                    'test_api_key',
                    'test_client_code',
                    'test_feed_token'
                )
    
    @pytest.mark.asyncio
    async def test_logout_success(self, mock_env_vars):
        with patch('angel_api.AuthenticationManager') as mock_auth_manager:
            mock_auth_instance = Mock()
            mock_auth_manager.return_value = mock_auth_instance
            
            # Mock async method
            async def mock_ensure_valid_session():
                return True
            mock_auth_instance.ensure_valid_session = mock_ensure_valid_session
            
            # Mock SmartConnect instance
            mock_smart_api = Mock()
            mock_auth_instance.smart_api = mock_smart_api
            mock_smart_api.terminateSession.return_value = {'status': True}
            
            client = AngelOneClient()
            result = await client.logout()
            
            assert result['status'] == 'success'
            assert result['message'] == 'Logout successful'
            mock_smart_api.terminateSession.assert_called_once_with('test_client_code')

if __name__ == "__main__":
    pytest.main([__file__])