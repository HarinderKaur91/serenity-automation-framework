package starter.pageobjects.herokuapp;

import net.serenitybdd.annotations.DefaultUrl;
import net.serenitybdd.core.pages.PageObject;
import org.openqa.selenium.By;
import org.openqa.selenium.support.ui.Select;

@DefaultUrl("https://the-internet.herokuapp.com/dropdown")
public class DropdownPage extends PageObject {

    public static final By DROPDOWN = By.id("dropdown");

    public void selectByVisibleText(String text) {
        new Select(getDriver().findElement(DROPDOWN)).selectByVisibleText(text);
    }

    public String selectedOption() {
        return new Select(getDriver().findElement(DROPDOWN))
                .getFirstSelectedOption().getText();
    }
}
