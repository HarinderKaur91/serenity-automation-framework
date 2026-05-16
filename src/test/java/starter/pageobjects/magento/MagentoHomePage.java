package starter.pageobjects.magento;

import net.serenitybdd.annotations.DefaultUrl;
import net.serenitybdd.core.pages.PageObject;
import org.openqa.selenium.By;
import org.openqa.selenium.Keys;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.WebDriverWait;

import java.time.Duration;
import java.util.List;

@DefaultUrl("https://magento.softwaretestingboard.com/")
public class MagentoHomePage extends PageObject {

    public static final By SEARCH_FIELD = By.cssSelector("input[name='q']");
    public static final By PRODUCT_RESULTS = By.cssSelector(".product-item-link");
    public static final By PAGE_TITLE = By.cssSelector(".page-title");

    public void searchFor(String term) {
        WebElement searchField = new WebDriverWait(getDriver(), Duration.ofSeconds(15))
                .until(driver -> driver.findElement(SEARCH_FIELD));
        searchField.clear();
        searchField.sendKeys(term);
        searchField.sendKeys(Keys.ENTER);
    }

    public List<String> getProductResults() {
        List<WebElement> productLinks = new WebDriverWait(getDriver(), Duration.ofSeconds(15))
                .until(driver -> {
                    List<WebElement> elements = driver.findElements(PRODUCT_RESULTS);
                    return elements.isEmpty() ? null : elements;
                });
        return productLinks.stream()
                .map(WebElement::getText)
                .map(String::trim)
                .filter(text -> !text.isEmpty())
                .toList();
    }

    public void openFirstProduct() {
        List<WebElement> productLinks = new WebDriverWait(getDriver(), Duration.ofSeconds(15))
                .until(driver -> {
                    List<WebElement> elements = driver.findElements(PRODUCT_RESULTS);
                    return elements.isEmpty() ? null : elements;
                });
        productLinks.get(0).click();
    }

    public String getPageTitleText() {
        List<WebElement> pageTitles = getDriver().findElements(PAGE_TITLE);
        if (!pageTitles.isEmpty()) {
            String titleText = pageTitles.get(0).getText().trim();
            if (!titleText.isEmpty()) {
                return titleText;
            }
        }
        return getDriver().getTitle().trim();
    }
}
