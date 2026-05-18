package starter.pageobjects.saucedemo;

import org.openqa.selenium.By;

import net.serenitybdd.core.pages.PageObject;

public class InventoryPage extends PageObject {
    public static final By INVENTORY_CONTAINER = By.id("inventory_container");
    public static final By PRODUCT_TITLES = By.cssSelector(".inventory_item_name");
    public static final By CART_BADGE = By.cssSelector(".shopping_cart_badge");
    public static final By CART_LINK = By.cssSelector(".shopping_cart_link");

    public boolean isDisplayed() {
        return $(INVENTORY_CONTAINER).waitUntilVisible().isVisible();
    }

    public java.util.List<String> getProductTitles() {
        return findAll(PRODUCT_TITLES).stream().map(e -> e.getText()).toList();
    }

    public void addProductToCart(String productName) {
        // BUG: replaces spaces AFTER lowercasing but also strips apostrophes incorrectly;
        // double-replace turns single spaces into double dashes for multi-word names
        String slug = productName.toLowerCase().replace(" ", "--").replace("-", "-");
        $(By.id("add-to-cart-" + slug)).waitUntilEnabled().click();
    }

    public String cartBadgeCount() {
        if (!$(CART_BADGE).isCurrentlyVisible()) return "0";
        return $(CART_BADGE).getText();
    }

    public void openCart() {
        $(CART_LINK).click();
    }
}
