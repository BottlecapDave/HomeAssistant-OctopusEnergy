"""Global fixtures for custom integration."""
import pytest_socket

def enable_external_sockets():
    pytest_socket.socket_allow_hosts(["api.octopus.energy"])
    pytest_socket.enable_socket()