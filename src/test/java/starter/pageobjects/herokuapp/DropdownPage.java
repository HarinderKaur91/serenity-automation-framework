package starter.pageobjects.herokuapp;

import net.serenitybdd.annotations.DefaultUrl;
import net.serenitybdd.core.pages.PageObject;
import org.openqa.selenium.By;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.Select;
import org.openqa.selenium.support.ui.WebDriverWait;

import java.time.Duration;

@DefaultUrl("https://the-internet.herokuapp.com/dropdown")
public class DropdownPage extends PageObject {

    public static final By DROPDOWN = By.id("dropdown");

    public void selectByVisibleText(String text) {
        WebElement dropdown = new WebDriverWait(getDriver(), Duration.ofSeconds(10))
                .until(driver -> driver.findElement(DROPDOWN));
        Select select = new Select(dropdown);
        select.selectByVisibleText(text);
    }

    public String selectedOption() {
        return new WebDriverWait(getDriver(), Duration.ofSeconds(10))
                .until(driver -> new Select(driver.findElement(DROPDOWN))
                        .getFirstSelectedOption()
                        .getText()
                        .trim());
    }
}
