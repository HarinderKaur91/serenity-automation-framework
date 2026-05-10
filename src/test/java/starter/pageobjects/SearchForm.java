package starter.pageobjects;

import net.serenitybdd.annotations.DefaultUrl;
import net.serenitybdd.core.pages.PageObject;
import org.openqa.selenium.By;

@DefaultUrl("https://duckduckgo.com/")
public class SearchForm extends PageObject {
    // DuckDuckGo updated their search input to use a data-ssg-id attribute in 2024+.
    // If this selector breaks, inspect the DuckDuckGo homepage for the current search input element.
    public static final By SEARCH_FIELD = By.cssSelector("[data-ssg-id='ai-searchbox-input']");
    public static final By ARTICLE_HEADINGS = By.cssSelector("a[data-testid='result-title-a']");
}
