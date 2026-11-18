"""Page Objects de saucedemo.com (patron Page Object Model)."""

from pages.cart_page import CartPage
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage

__all__ = ["CartPage", "InventoryPage", "LoginPage"]
