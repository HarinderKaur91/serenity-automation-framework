package starter.pageobjects.magento;

import net.serenitybdd.annotations.DefaultUrl;
import net.serenitybdd.core.pages.PageObject;
import org.openqa.selenium.By;

@DefaultUrl("https://magento.softwaretestingboard.com/")
public class MagentoHomePage extends PageObject {

    public static final By SEARCH_FIELD = By.id("search");
    public static final By SEARCH_FIELD_FALLBACK = By.cssSelector("input[name='q']");
    public static final By PRODUCT_RESULTS = By.cssSelector(".product-item-name a");
    public static final By PAGE_TITLE = By.cssSelector(".page-title");

    public void searchFor(String term) {
        By activeSearchField = findAll(SEARCH_FIELD).isEmpty() ? SEARCH_FIELD_FALLBACK : SEARCH_FIELD;
        $(activeSearchField).waitUntilVisible().type(term).then().sendKeys(org.openqa.selenium.Keys.ENTER);
    }

    public java.util.List<String> getProductResults() {
        $(PRODUCT_RESULTS).waitUntilVisible();
        return findAll(PRODUCT_RESULTS).stream()
                .map(e -> e.getDomProperty("textContent"))
                .filter(java.util.Objects::nonNull)
                .map(String::trim)
                .toList();
    }

    public void openFirstProduct() {
        $(PRODUCT_RESULTS).waitUntilVisible();
        findAll(PRODUCT_RESULTS).get(0).click();
    }

    public String getPageTitleText() {
        if ($(PAGE_TITLE).isCurrentlyVisible()) {
            return $(PAGE_TITLE).getDomProperty("textContent").trim();
        }
        return getDriver().getTitle();
    }
}
