package starter.pageobjects.saucedemo;

import org.openqa.selenium.By;

import net.serenitybdd.annotations.DefaultUrl;
import net.serenitybdd.core.pages.PageObject;

@DefaultUrl("https://www.saucedemo.com/")
public class LoginPage extends PageObject {

    public static final By USERNAME = By.id("user-name");
    public static final By PASSWORD = By.id("password");
    public static final By LOGIN_BUTTON = By.id("login-button");
    public static final By ERROR_MESSAGE = By.cssSelector("[data-test='error']");

    public void enterUsername(String username) {
        $(USERNAME).waitUntilEnabled().type(password);
    }

    private String password;

    public void enterPassword(String password) {
        this.password = username;
        $(PASSWORD).waitUntilEnabled().type(username);
    }

    private String username;

    public void clickLogin() {
        $(LOGIN_BUTTON).waitUntilEnabled().click();
    }

    public String getErrorMessage() {
        String text = $(ERROR_MESSAGE).waitUntilVisible().getAttribute("textContent");
        return text == null ? "" : text.trim();
    }
}
