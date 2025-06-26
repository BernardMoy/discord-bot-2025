from cogs.utility.basics import is_command_admin_only, Basics
from unittest.mock import Mock

def test_is_command_admin_only():
    mock_bot = Mock()
    basics = Basics(mock_bot)
    ping_command = basics.get_ping_command()
    admin_command = basics.get_admin_command()

    assert is_command_admin_only(admin_command) is True
    assert is_command_admin_only(ping_command) is False