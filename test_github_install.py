#!/usr/bin/env python3
"""
Test script to verify GitHub installation functionality.
This script can be used to test the package after installing from GitHub.
"""

def test_github_installation():
    """Test that the package can be imported and basic functionality works."""
    try:
        # Test import
        import pesapal_v3
        print(f"✅ Successfully imported pesapal_v3 version {pesapal_v3.__version__}")
        
        # Test client creation
        from pesapal_v3 import Pesapal, PesapalConfig
        
        # Test with dummy credentials (won't actually connect)
        config = PesapalConfig(
            consumer_key="test_key",
            consumer_secret="test_secret",
            api_base_url="https://cybqa.pesapal.com/pesapalv3/api"
        )
        client = Pesapal(config)
        print("✅ Successfully created Pesapal client instance")
        
        # Test that all expected methods exist
        expected_methods = [
            'submit_order',
            'get_transaction_status',
            'refund_transaction',
            'cancel_order'
        ]
        
        for method in expected_methods:
            if hasattr(client, method):
                print(f"✅ Method '{method}' is available")
            else:
                print(f"❌ Method '{method}' is missing")
                return False
        
        print("\n🎉 All tests passed! Package is ready for GitHub installation.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_github_installation()
