package starter.pageobjects.magento;

import net.serenitybdd.annotations.DefaultUrl;
import net.serenitybdd.core.pages.PageObject;
import org.openqa.selenium.By;

@DefaultUrl("https://magento.softwaretestingboard.com/")
public class MagentoHomePage extends PageObject {

    public static final By SEARCH_FIELD = By.id("search");
    public static final By PRODUCT_RESULTS = By.cssSelector(".product-item-name a");
    public static final By PAGE_TITLE = By.cssSelector(".page-title");

    public void searchFor(String term) {
        $(SEARCH_FIELD).waitUntilEnabled().type(term);
        $(SEARCH_FIELD).sendKeys(org.openqa.selenium.Keys.ENTER);
    }

    public java.util.List<String> getProductResults() {
        $(PRODUCT_RESULTS).waitUntilVisible();
        return findAll(PRODUCT_RESULTS).stream()
                .map(e -> e.getText())
                .collect(java.util.stream.Collectors.toList());
    }

    public void openFirstProduct() {
        $(PRODUCT_RESULTS).waitUntilVisible();
        findAll(PRODUCT_RESULTS).get(0).click();
    }

    public String getPageTitleText() {
        $(PRODUCT_RESULTS).waitUntilVisible();
        return getDriver().getTitle();
    }
}
