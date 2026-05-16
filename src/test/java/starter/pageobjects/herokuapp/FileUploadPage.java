package starter.pageobjects.herokuapp;

import net.serenitybdd.annotations.DefaultUrl;
import net.serenitybdd.core.pages.PageObject;
import org.openqa.selenium.By;

@DefaultUrl("https://the-internet.herokuapp.com/upload")
public class FileUploadPage extends PageObject {

    public static final By FILE_INPUT = By.id("file-upload");
    public static final By SUBMIT_BUTTON = By.id("file-submit");
    public static final By UPLOADED_FILES = By.id("uploaded-files");

    public void selectFile(String absolutePath) {
        $(FILE_INPUT).sendKeys(absolutePath);
    }

    public void submit() {
        $(SUBMIT_BUTTON).click();
    }

    public String uploadedFileName() {
        return $(UPLOADED_FILES).waitUntilVisible().getDomProperty("textContent").trim();
    }
}
