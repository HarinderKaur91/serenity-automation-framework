package starter.actions;

import net.serenitybdd.annotations.Step;
import net.serenitybdd.core.steps.UIInteractionSteps;
import org.openqa.selenium.Keys;
import starter.pageobjects.SearchForm;

import java.time.Duration;
import java.util.List;

import static org.openqa.selenium.support.ui.ExpectedConditions.titleContains;

public class SearchSteps extends UIInteractionSteps {

    SearchForm searchForm;

    @Step("User searches for '{0}'")
    public void searchForTerm(String searchTerm) {
        find(SearchForm.SEARCH_FIELD).sendKeys(searchTerm, Keys.ENTER);
        withTimeoutOf(Duration.ofSeconds(10))
                .waitFor(titleContains(searchTerm));
    }

    @Step("Check the search results")
    public List<String> getSearchResults() {
        return findAll(SearchForm.ARTICLE_HEADINGS).texts();
    }
}
