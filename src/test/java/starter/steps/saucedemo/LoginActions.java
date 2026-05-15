package starter.steps.saucedemo;

import net.serenitybdd.annotations.Step;
import starter.pageobjects.saucedemo.CheckoutPage;
import starter.pageobjects.saucedemo.InventoryPage;
import starter.pageobjects.saucedemo.LoginPage;

import java.util.List;

public class LoginActions {

    LoginPage loginPage;
    InventoryPage inventoryPage;
    CheckoutPage checkoutPage;

    @Step("Open the SauceDemo login page")
    public void openLoginPage() {
        loginPage.open();
        loginPage.getDriver().manage().deleteAllCookies();
        loginPage.evaluateJavascript("window.localStorage.clear(); window.sessionStorage.clear();");
        loginPage.open();
    }

    @Step("Log in as {0}")
    public void loginAs(String username, String password) {
        loginPage.enterUsername(username);
        loginPage.enterPassword(password);
        loginPage.clickLogin();
    }

    @Step("Read the login error message")
    public String errorMessage() {
        return loginPage.getErrorMessage();
    }

    @Step("Check the inventory page is displayed")
    public boolean inventoryIsDisplayed() {
        return inventoryPage.isDisplayed();
    }

    @Step("Read the product titles")
    public List<String> productTitles() {
        return inventoryPage.getProductTitles();
    }

    @Step("Add product {0} to the cart")
    public void addProductToCart(String productName) {
        inventoryPage.addProductToCart(productName);
    }

    @Step("Read the cart badge count")
    public String cartBadgeCount() {
        return inventoryPage.cartBadgeCount();
    }

    @Step("Open the shopping cart")
    public void openCart() {
        inventoryPage.openCart();
    }

    @Step("Read the number of items currently in the cart")
    public int cartItemCount() {
        return checkoutPage.cartItemCount();
    }

    @Step("Complete the checkout for {0} {1} (zip {2})")
    public void completeCheckout(String firstName, String lastName, String zip) {
        checkoutPage.clickCheckout();
        checkoutPage.fillCustomerInfo(firstName, lastName, zip);
        checkoutPage.finishCheckout();
    }

    @Step("Read the order confirmation header")
    public String confirmationMessage() {
        return checkoutPage.confirmationMessage();
    }
}
