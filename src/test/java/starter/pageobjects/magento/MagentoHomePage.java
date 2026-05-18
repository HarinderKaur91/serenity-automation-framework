package starter.pageobjects.magento;

import net.serenitybdd.annotations.DefaultUrl;
import net.serenitybdd.core.pages.PageObject;
import net.serenitybdd.core.pages.WebElementFacade;
import org.openqa.selenium.By;
import org.openqa.selenium.NoSuchElementException;
import org.openqa.selenium.TimeoutException;

import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.function.Supplier;

@DefaultUrl("https://magento.softwaretestingboard.com/")
public class MagentoHomePage extends PageObject {

    public static final By PRODUCT_RESULTS = By.cssSelector(".product-item-name a");
    public static final By PAGE_TITLE = By.cssSelector(".page-title");
    private static final By LOADING_MASK = By.cssSelector(".loading-mask");
    private static final String SEARCH_RESULTS_URL = "https://magento.softwaretestingboard.com/catalogsearch/result/?q=";
    private static final int MAX_SSL_ERROR_RETRIES = 3;
    private String lastSearchTerm;

    public void searchFor(String term) {
        lastSearchTerm = term;
        String encodedTerm = URLEncoder.encode(term, StandardCharsets.UTF_8);
        getDriver().navigate().to(SEARCH_RESULTS_URL + encodedTerm);
        waitForLoadingToComplete();
    }

    private void waitForLoadingToComplete() {
        try {
            WebElementFacade mask = $(LOADING_MASK);
            if (mask.isPresent() && mask.isCurrentlyVisible()) {
                mask.waitUntilNotVisible();
            }
        } catch (TimeoutException | NoSuchElementException ignored) {
            // Loading mask may not always be present or may already be gone; proceed regardless
        }
    }

    public java.util.List<String> getProductResults() {
        return withCloudflareRetry(() -> {
            $(PRODUCT_RESULTS).waitUntilVisible();
            java.util.List<WebElementFacade> elements = findAll(PRODUCT_RESULTS);
            if (elements == null) return java.util.Collections.emptyList();
            return elements.stream()
                    .map(WebElementFacade::getText)
                    .filter(t -> t != null && !t.isEmpty())
                    .toList();
        });
    }

    public void openFirstProduct() {
        withCloudflareRetry(() -> {
            $(PRODUCT_RESULTS).waitUntilVisible();
            findAll(PRODUCT_RESULTS).get(0).click();
            return null;
        });
    }

    public String getPageTitleText() {
        return withCloudflareRetry(() -> {
            $(PAGE_TITLE).waitUntilVisible();
            String title = getDriver().getTitle();
            return title == null ? "" : title;
        });
    }

    private <T> T withCloudflareRetry(Supplier<T> action) {
        RuntimeException lastException = null;
        for (int attempt = 1; attempt <= MAX_SSL_ERROR_RETRIES; attempt++) {
            try {
                return action.get();
            } catch (NoSuchElementException | TimeoutException e) {
                lastException = e;
                if (!isCloudflareSslErrorPage() || lastSearchTerm == null || attempt == MAX_SSL_ERROR_RETRIES) {
                    throw e;
                }
                searchFor(lastSearchTerm);
            }
        }
        throw lastException;
    }

    private boolean isCloudflareSslErrorPage() {
        String title = getDriver().getTitle();
        if (title != null && title.contains("526: Invalid SSL certificate")) {
            return true;
        }
        String pageSource = getDriver().getPageSource();
        return pageSource != null
                && pageSource.contains("Error code 526")
                && pageSource.contains("cf-error-details");
    }
}
